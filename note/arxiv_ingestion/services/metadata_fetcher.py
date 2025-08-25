import asyncio
from typing import Any, Dict, List, Optional

from arxiv_ingestion.db.factory import make_database
from arxiv_ingestion.db.models import Paper  # SQLAlchemy ORM model
from arxiv_ingestion.services.arxiv_client import ArxivClient
from arxiv_ingestion.services.pdf_parser import PDFParserService
from arxiv_ingestion.services.schemas import ArxivMetadata, ArxivPaper, ParsedPaper
from dateutil import parser
from logger import get_logger

logger = get_logger(__name__)


class MetadataFetcher:
    def __init__(self, arxiv_client: ArxivClient, pdf_parser: PDFParserService):
        self.arxiv_client = arxiv_client
        self.pdf_parser = pdf_parser
        self.database = make_database()
        self.max_concurrent_downloads: int = 5
        self.max_concurrent_parsing: int = 3

    # ------------------------------
    # Stage 1: Fetch metadata
    # ------------------------------
    async def fetch_papers(
        self, target_date: str, max_results: int = 5
    ) -> List[ArxivPaper]:
        papers = await self.arxiv_client.fetch_papers(
            max_results=max_results, from_date=target_date, to_date=target_date
        )
        print(f"[fetch_papers] Fetched {len(papers)} papers from arXiv")
        return papers

    # ------------------------------
    # Stage 2: Download & parse PDF
    # ------------------------------

    async def process_pdfs_batch(
        self, papers: List[ArxivPaper], download_pdfs: bool
    ) -> Dict[str, Any]:
        results = {
            "downloaded": 0,
            "parsed": 0,
            "parsed_papers": {},
            "errors": [],
            "download_failures": [],
            "parse_failures": [],
            "updated_papers": papers,
        }

        print(f"Starting async pipeline for {len(papers)} PDFs...")
        print(f"Concurrent downloads: {self.max_concurrent_downloads}")
        print(f"Concurrent parsing: {self.max_concurrent_parsing}")

        # Create semaphores for controlled concurrency
        download_semaphore = asyncio.Semaphore(self.max_concurrent_downloads)
        parse_semaphore = asyncio.Semaphore(self.max_concurrent_parsing)

        # Start all download+parse pipelines concurrently
        # pipeline_tasks = [self._download_and_parse_pipeline(paper, download_semaphore, parse_semaphore) for paper in papers]
        pipeline_tasks = [
            self._download_and_parse_pipeline(
                idx, paper, download_semaphore, parse_semaphore, download_pdfs
            )
            for idx, paper in enumerate(papers)
        ]

        # Wait for all pipelines to complete
        pipeline_results = await asyncio.gather(*pipeline_tasks, return_exceptions=True)

        # Process results with detailed error tracking
        for paper, result in zip(papers, pipeline_results):
            if isinstance(result, Exception):
                error_msg = f"Pipeline error for {paper.arxiv_id}: {str(result)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
            elif result:
                # Result is tuple: (download_success, parsed_paper)
                idx, download_success, parsed_success, pdf_path, parsed_paper = result

                paper = papers[idx]  # 用 idx 確保對應正確
                paper.pdf_cached_path = pdf_path
                paper.pdf_downloaded = download_success
                paper.pdf_parsed = parsed_success

                if download_success:
                    results["downloaded"] += 1

                    if parsed_paper:
                        results["parsed"] += 1
                        results["parsed_papers"][paper.arxiv_id] = parsed_paper
                    else:
                        # Download succeeded but parsing failed
                        results["parse_failures"].append(paper.arxiv_id)
                else:
                    # Download failed
                    results["download_failures"].append(paper.arxiv_id)
            else:
                # No result returned (shouldn't happen but handle gracefully)
                results["download_failures"].append(paper.arxiv_id)

        # Simple processing summary
        print(
            f"PDF processing: {results['downloaded']}/{len(papers)} downloaded, {results['parsed']} parsed"
        )

        if results["download_failures"]:
            logger.warning(f"Download failures: {len(results['download_failures'])}")

        if results["parse_failures"]:
            logger.warning(f"Parse failures: {len(results['parse_failures'])}")

        # Add specific failure info to general errors list for backward compatibility
        if results["download_failures"]:
            results["errors"].extend(
                [
                    f"Download failed: {arxiv_id}"
                    for arxiv_id in results["download_failures"]
                ]
            )
        if results["parse_failures"]:
            results["errors"].extend(
                [
                    f"PDF parse failed: {arxiv_id}"
                    for arxiv_id in results["parse_failures"]
                ]
            )

        return results

    async def _download_and_parse_pipeline(
        self,
        idx: int,
        paper: ArxivPaper,
        download_semaphore: asyncio.Semaphore,
        parse_semaphore: asyncio.Semaphore,
        download_pdfs: bool,
    ) -> tuple[int, bool, bool, Optional[str], Optional[ParsedPaper]]:
        download_success = False
        parsed_success = False
        parsed_paper = None
        pdf_path = None

        try:
            # Step 1: Download PDF with download concurrency control
            async with download_semaphore:
                print(f"Starting download: {paper.arxiv_id} with {download_pdfs} ")
                pdf_path = await self.arxiv_client.download_pdf(
                    paper, force_download=download_pdfs
                )

                if pdf_path:
                    download_success = True
                    print(f"Download complete: {paper.arxiv_id} in {pdf_path}")
                else:
                    logger.error(f"Download failed: {paper.arxiv_id}")
                    return (idx, False, False, None, None)

            # Step 2: Parse PDF with parse concurrency control (happens AFTER download completes)
            # This allows other downloads to continue while this PDF is being parsed
            async with parse_semaphore:
                logger.debug(f"Starting parse: {paper.arxiv_id}")
                pdf_content = await self.pdf_parser.parse_pdf(
                    paper.arxiv_id, save_img_local=download_pdfs
                )

                if pdf_content:
                    parsed_success = True
                    # Create ArxivMetadata from the paper
                    arxiv_metadata = ArxivMetadata(
                        title=paper.title,
                        authors=paper.authors,
                        abstract=paper.abstract,
                        arxiv_id=paper.arxiv_id,
                        categories=paper.categories,
                        published_date=paper.published_date,
                        pdf_url=paper.pdf_url,
                    )

                    # Combine into ParsedPaper
                    parsed_paper = ParsedPaper(
                        arxiv_metadata=arxiv_metadata, pdf_content=pdf_content
                    )
                    logger.debug(
                        f"Parse complete: {paper.arxiv_id} - {len(pdf_content.raw_text)} chars extracted"
                    )
                else:
                    # PDF parsing failed, but this is not critical - we can continue with metadata only
                    logger.warning(
                        f"PDF parsing failed for {paper.arxiv_id}, continuing with metadata only"
                    )

        except Exception as e:
            logger.error(f"Pipeline error for {paper.arxiv_id}: {e}")
        return (idx, download_success, parsed_success, pdf_path, parsed_paper)

    # ------------------------------
    # Stage 3: Store to DB
    # ------------------------------
    def store_to_db(self, papers: List[ArxivPaper]) -> int:
        stored_count = 0
        with self.database.get_session() as session:
            for paper in papers:
                try:
                    # 用 ORM 建立或更新
                    obj = (
                        session.query(Paper).filter_by(arxiv_id=paper.arxiv_id).first()
                    )
                    if not obj:
                        obj = Paper(arxiv_id=paper.arxiv_id)
                        session.add(obj)

                    # 更新欄位
                    obj.title = paper.title
                    obj.authors = paper.authors or []
                    obj.abstract = paper.abstract
                    obj.categories = paper.categories or []

                    # str -> date

                    obj.published_date = (
                        parser.isoparse(paper.published_date).date()
                        if paper.published_date
                        else None
                    )
                    obj.updated_date = (
                        parser.isoparse(paper.updated_date).date()
                        if paper.updated_date
                        else None
                    )

                    obj.pdf_url = paper.pdf_url

                    # Path -> str
                    obj.pdf_cached_path = (
                        str(paper.pdf_cached_path) if paper.pdf_cached_path else None
                    )

                    obj.pdf_downloaded = paper.pdf_downloaded or False
                    obj.pdf_parsed = paper.pdf_parsed or False

                    stored_count += 1
                except Exception as e:
                    logger.error(f"Failed to store {paper.arxiv_id} in DB: {e}")

            session.commit()
            print(f"[store_to_db] Stored {stored_count} papers to DB")
            return stored_count
