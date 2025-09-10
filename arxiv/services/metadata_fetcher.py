import asyncio
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional

from dateutil import parser as date_parser
from db.factory import make_database
from db.PaperRepository import PaperRepository
from db.storage_metrics import monitored_db
from logger import AppLogger
from services.arxiv_client import ArxivClient
from services.pdf_parser import PDFParserService
from services.schemas import ArxivMetadata, ArxivPaper, ParsedPaper

logger = AppLogger(__name__).get_logger()


@lru_cache(maxsize=1)
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

    async def process_pdfs_batch(self, papers: List[ArxivPaper]) -> Dict[str, Any]:
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
        pipeline_tasks = [
            self._download_and_parse_pipeline(
                paper, download_semaphore, parse_semaphore
            )
            for paper in papers
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
                download_success, parsed_paper = result

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
        paper: ArxivPaper,
        download_semaphore: asyncio.Semaphore,
        parse_semaphore: asyncio.Semaphore,
    ) -> tuple[int, bool, bool, Optional[str], Optional[ParsedPaper]]:
        download_success = False
        parsed_paper = False

        try:
            # Step 1: Download PDF with download concurrency control
            async with download_semaphore:
                print(f"Starting download: {paper.arxiv_id} ")
                pdf_path = await self.arxiv_client.download_pdf(
                    paper, force_download=True, force_upload_cloud=False
                )

                if pdf_path:
                    download_success = True
                    print(f"Download complete: {paper.arxiv_id} in {pdf_path}")
                else:
                    logger.error(f"Download failed: {paper.arxiv_id}")
                    return (False, False)

            # Step 2: Parse PDF with parse concurrency control (happens AFTER download completes)
            # This allows other downloads to continue while this PDF is being parsed
            async with parse_semaphore:
                logger.debug(f"Starting parse: {paper.arxiv_id}")
                # Structured content with text, tables, figures
                pdf_content = await self.pdf_parser.parse_pdf(
                    pdf_path
                )  # TODO: so far need force_download = True

                # pdf_content = await self.pdf_parser.parse2pdf(
                #     pdf_path
                # )  # TODO:  happened failed Docling parsing returned no result,  Skipping PDF processing due to size/page limits: PDF file too large:
                if pdf_content:
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
        return (download_success, parsed_paper)

    # ------------------------------
    # Stage 3: Store to DB
    # ------------------------------
    @monitored_db
    def store_to_db(
        self,
        papers: List[ArxivPaper],
        parsed_papers: Dict[str, ParsedPaper],
    ) -> int:
        """
        Store papers and parsed content to database with comprehensive content storage.

        Args:
            papers: List of ArxivPaper metadata
            parsed_papers: Dictionary of parsed PDF content by arxiv_id

        Returns:
            Number of papers stored successfully
        """
        stored_count = 0
        with self.database.get_session() as session:
            repo = PaperRepository(session)
            for paper in papers:
                try:
                    logger.info(f"paper.arxiv_id {paper.arxiv_id}")
                    parsed_paper = parsed_papers.get(paper.arxiv_id)
                    published_date = (
                        date_parser.parse(paper.published_date)
                        if isinstance(paper.published_date, str)
                        else paper.published_date
                    )
                    paper_data = {
                        "arxiv_id": paper.arxiv_id,
                        "title": paper.title,
                        "authors": paper.authors,
                        "abstract": paper.abstract,
                        "categories": paper.categories,
                        "published_date": published_date,
                        "pdf_url": paper.pdf_url,
                    }

                    # Add parsed content if available
                    if parsed_paper:
                        parsed_content = self._serialize_parsed_content(parsed_paper)
                        paper_data.update(parsed_content)
                        logger.debug(
                            f"Storing paper {paper.arxiv_id} with parsed content ({len(parsed_content.get('raw_text', '')) if parsed_content.get('raw_text') else 0} chars)"
                        )
                    else:
                        # No parsed content - just store metadata
                        paper_data.update(
                            {
                                "pdf_processed": False,
                                "parser_metadata": {
                                    "note": "PDF processing not available or failed"
                                },
                            }
                        )
                        logger.debug(
                            f"Storing paper {paper.arxiv_id} with metadata only"
                        )

                    repo.upsert_paper(paper_data)
                    stored_count += 1
                except Exception as e:
                    logger.error(f"Failed to store {paper.arxiv_id} in DB: {e}")

            session.commit()
            print(f"[store_to_db] Stored {stored_count} papers to DB")
            return stored_count

    def _serialize_parsed_content(self, parsed_paper: ParsedPaper) -> Dict[str, Any]:
        """Serialize ParsedPaper content for database storage.

        :param parsed_paper: ParsedPaper object with PDF content
        :type parsed_paper: ParsedPaper
        :returns: Dictionary with serialized content for database storage
        :rtype: Dict[str, Any]
        """
        try:
            pdf_content = parsed_paper.pdf_content

            # Serialize sections
            sections = [
                {"title": section.title, "content": section.content}
                for section in pdf_content.sections
            ]

            # Serialize references
            references = list(pdf_content.references)  #

            return {
                "raw_text": pdf_content.raw_text,
                "sections": sections,
                "references": references,
                "parser_used": (
                    pdf_content.parser_used.value if pdf_content.parser_used else None
                ),
                "parser_metadata": pdf_content.metadata or {},
                "pdf_processed": True,
                "pdf_processing_date": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Failed to serialize parsed content: {e}")
            return {"pdf_processed": False, "parser_metadata": {"error": str(e)}}
