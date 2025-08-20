# services/arxiv_client.py
import asyncio

import time
from pathlib import Path
from dateutil import parser
from typing import List, Optional
from datetime import datetime
from urllib.parse import quote, urlencode
import httpx
import xml.etree.ElementTree as ET

from arxiv_ingestion.exceptions import ArxivAPIException, ArxivAPITimeoutError
from arxiv_ingestion.config import ArxivSettings
from arxiv_ingestion.db.minio import s3_client
from arxiv_ingestion.config import MINIO_BUCKET
from arxiv_ingestion.services.schemas import ArxivPaper
from logger import get_logger

logger = get_logger(__name__)


class ArxivClient:

    def __init__(self, settings: ArxivSettings):

        self.pdf_cache_dir = Path(settings.pdf_cache_dir)
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)

        self._last_request_time: Optional[float] = None

        self.cache_dir = Path(settings.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = settings.api_base_url
        self.category = settings.search_category
        self.max_results = settings.max_results
        self.timeout_seconds = settings.timeout_seconds
        self.rate_limit_delay = settings.rate_limit_delay
        self._last_request: Optional[datetime] = None

    async def fetch_papers(
        self,
        max_results: int = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        start: int = 0,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> List[ArxivPaper]:
        """Fetch paper metadata from arXiv."""
        if self._last_request:
            delta = (datetime.now() - self._last_request).total_seconds()
            if delta < self.RATE_LIMIT:
                await asyncio.sleep(self.RATE_LIMIT - delta)

        if max_results is None:
            max_results = self.max_results

        query = f"cat:{self.category}"

        if from_date or to_date:
            # Convert dates to arXiv format (YYYYMMDDHHMM) - use 0000 for start of day, 2359 for end
            date_from = f"{from_date}0000" if from_date else "*"
            date_to = f"{to_date}2359" if to_date else "*"
            # Use correct arXiv API syntax with + symbols
            query += f" AND submittedDate:[{date_from}+TO+{date_to}]"

        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        # url = f"{self.base_url}?{httpx.QueryParams(params)}"

        safe = ":+[]"  # Don't encode :, +, [, ] characters needed for arXiv queries
        url = f"{self.base_url}?{urlencode(params, quote_via=quote, safe=safe)}"

        # rate limit
        if self._last_request_time:
            delta = time.time() - self._last_request_time
            if delta < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - delta)

        self._last_request_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                xml_data = resp.text

            # with open("output.xml", "w", encoding="utf-8") as f:
            #     f.write(xml_data)
            papers = self._parse_xml(xml_data)
            logger.info(f"Query returned {len(papers)} papers")
            return papers

        except httpx.TimeoutException as e:
            logger.error(f"arXiv API timeout: {e}")
            raise ArxivAPITimeoutError(f"arXiv API request timed out: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"arXiv API HTTP error: {e}")
            raise ArxivAPIException(
                f"arXiv API returned error {e.response.status_code}: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to fetch papers from arXiv: {e}")
            raise ArxivAPIException(f"Unexpected error fetching papers from arXiv: {e}")

    def _parse_xml(self, xml_text: str) -> List[ArxivPaper]:
        """Parse arXiv API XML response to list of ArxivPaper."""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")
            return []

        papers: List[ArxivPaper] = []

        for entry in root.findall("atom:entry", ns):
            try:
                # arXiv ID
                id_elem = entry.find("atom:id", ns)
                if id_elem is None or not id_elem.text:
                    continue
                arxiv_id = id_elem.text.split("/")[-1]

                # 標題
                title_elem = entry.find("atom:title", ns)
                title = title_elem.text.strip() if title_elem is not None else ""

                # 摘要
                abstract_elem = entry.find("atom:summary", ns)
                abstract = (
                    abstract_elem.text.strip() if abstract_elem is not None else ""
                )

                # 日期
                published_elem = entry.find("atom:published", ns)
                updated_elem = entry.find("atom:updated", ns)
                published_date = (
                    published_elem.text if published_elem is not None else None
                )
                updated_date = updated_elem.text if updated_elem is not None else None

                # 作者列表
                authors = []
                for author in entry.findall("atom:author", ns):
                    name_elem = author.find("atom:name", ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())

                # 分類
                categories = []
                for cat_elem in entry.findall("atom:category", ns):
                    term = cat_elem.attrib.get("term")
                    if term:
                        categories.append(term)

                # PDF URL
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                papers.append(
                    ArxivPaper(
                        arxiv_id=arxiv_id,
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        categories=categories,
                        published_date=published_date,
                        updated_date=updated_date,
                        pdf_url=pdf_url,
                    )
                )

            except Exception as e:
                logger.warning(f"Failed to parse entry: {e}")
                continue

        logger.info(f"Fetched {len(papers)} papers from arXiv")
        return papers

    async def download_pdf(
        self, paper: ArxivPaper, force_download: bool = False, max_retries: int = 3
    ) -> Optional[Path]:
        if not paper.pdf_url:
            logger.error(f"No PDF URL for paper {paper.arxiv_id}")
            return None

        # 構造安全檔名
        pdf_path = self.pdf_cache_dir / f"{paper.arxiv_id.replace('/', '_')}.pdf"
        object_name = f"{paper.arxiv_id}/{paper.arxiv_id}.pdf"

        # 若已有快取且不強制下載，直接回傳
        if pdf_path.exists() and not force_download:
            logger.info(f"Using cached PDF: {pdf_path.name}")
            return pdf_path

        # 尊重速率限制
        await asyncio.sleep(self.rate_limit_delay)

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout_seconds, follow_redirects=True
                ) as client:
                    async with client.stream("GET", paper.pdf_url) as response:
                        response.raise_for_status()
                        with open(pdf_path, "wb") as f:
                            async for chunk in response.aiter_bytes():
                                f.write(chunk)

                # 確認檔案存在後再上傳 MinIO
                if pdf_path.exists():
                    with open(pdf_path, "rb") as f:
                        s3_client.upload_fileobj(f, MINIO_BUCKET, object_name)

                logger.info(
                    f"Successfully downloaded PDF: {pdf_path.name} in {pdf_path}"
                )
                return pdf_path

            except (httpx.TimeoutException, httpx.HTTPError) as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(
                        f"Download attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {max_retries} attempts: {e}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected download error: {e}")
                return None

        # 若下載失敗，刪除部分檔案
        if pdf_path.exists():
            pdf_path.unlink()
        return None
