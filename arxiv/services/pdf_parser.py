import asyncio
import io
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
import pdfplumber
from config import MINIO_BUCKET
from db.minio import s3_client
from exceptions import PDFParsingException, PDFValidationError
from logger import AppLogger
from PIL import Image
from services.docling import DoclingParser
from services.schemas import (
    PaperFigure,
    PaperSection,
    PaperTable,
    ParserType,
    PdfContent,
)

logger = AppLogger(__name__).get_logger()


class TextExtractor:
    def extract_stream(self, pdf_stream: io.BytesIO) -> (List[PaperSection], List[str]):
        sections, all_text = [], []
        # pdfplumber 可以吃 BytesIO，不一定要檔案路徑
        with pdfplumber.open(pdf_stream) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    sections.append(
                        PaperSection(title=f"Page {i}", content=text, level=1)
                    )
                    all_text.append(text)
        return sections, all_text


class TableExtractor:
    def extract_stream(
        self, pdf_stream: io.BytesIO, pdf_filename: str
    ) -> List[PaperTable]:
        tables = []
        with pdfplumber.open(pdf_stream) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                for t_idx, _ in enumerate(page_tables, start=1):
                    tables.append(
                        PaperTable(
                            caption=f"Page {i} Table {t_idx}",
                            id=f"{pdf_filename}-p{i}-t{t_idx}",
                        )
                    )
        return tables


class FigureExtractor:
    def __init__(self, image_dir: str = "/data/arxiv_images"):
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def extract_stream(
        self,
        pdf_stream: io.BytesIO,
        pdf_filename: str,
        save_local: bool = True,
        upload_s3: bool = True,
    ) -> List[PaperFigure]:
        pdf_bytes = pdf_stream.read()
        pdf_stream.seek(0)  # 重置 stream
        return self._extract_internal(pdf_bytes, pdf_filename, save_local, upload_s3)

    def _extract_internal(
        self,
        pdf_bytes: bytes,
        pdf_filename: str,
        save_local: bool = True,
        upload_s3: bool = True,
    ) -> List[PaperFigure]:
        figures = []
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_idx in range(len(pdf_document)):
            page = pdf_document.load_page(page_idx)
            for img_idx, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                object_name = f"{pdf_filename}/p{page_idx + 1}-img{img_idx}.{image_ext}"
                image_path = self.image_dir / object_name
                image_path.parent.mkdir(parents=True, exist_ok=True)

                pil_image = Image.open(io.BytesIO(image_bytes))

                if save_local:
                    pil_image.save(image_path)

                if upload_s3:
                    buffer = io.BytesIO()
                    pil_image.save(buffer, format=pil_image.format or image_ext.upper())
                    buffer.seek(0)
                    s3_client.upload_fileobj(buffer, MINIO_BUCKET, object_name)

                figures.append(
                    PaperFigure(
                        caption=f"Page {page_idx + 1} Image {img_idx}",
                        id=f"s3://{MINIO_BUCKET}/{object_name}",
                    )
                )
        pdf_document.close()
        return figures


# --------------------------
# Service Orchestrator
# --------------------------


class PDFParserService:
    """PDF 解析服務：抽文字、表格與圖片"""

    def __init__(
        self,
        max_pages: int,
        max_file_size_mb: int,
        do_ocr: bool = False,
        do_table_structure: bool = True,
    ):
        """Initialize PDF parser service with configurable limits."""

        self.docling_parser = DoclingParser(
            max_pages=max_pages,
            max_file_size_mb=max_file_size_mb,
            do_ocr=do_ocr,
            do_table_structure=do_table_structure,
        )

        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.figure_extractor = FigureExtractor(image_dir="/data/arxiv_images")

    def _parse_pdf_sync(
        self, pdf_path: Path, save_img_local: bool
    ) -> Optional[PdfContent]:
        # object_name = f"{arxiv_id}/{arxiv_id}.pdf"  # MinIO 上的物件路徑

        # 檢查該資料夾 / 檔案是否存在
        # if not s3_file_exists(MINIO_BUCKET, object_name):
        #     logger.warning(f"No PDF found in MinIO for arxiv_id={arxiv_id}")
        #     return None
        # print(f"object_name {object_name}")
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise PDFValidationError(f"PDF file not found: {pdf_path}")

        try:
            with pdf_path.open("rb") as f:
                pdf_bytes = f.read()
                buffer = io.BytesIO(pdf_bytes)
                sections, all_text = self.text_extractor.extract_stream(buffer)
                buffer.seek(0)
                tables = self.table_extractor.extract_stream(buffer, pdf_path.stem)
                buffer.seek(0)
                figures = self.figure_extractor.extract_stream(
                    buffer, pdf_path.stem, save_local=save_img_local, upload_s3=True
                )
            return PdfContent(
                sections=sections,
                tables=tables,
                figures=figures,
                raw_text="\n".join(all_text),
                references=[],
                parser_used=ParserType.DOCLING,
                metadata={"pages": len(sections)},
            )

        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}", exc_info=True)
            return None

    async def parse_pdf(
        self, pdf_path: Path, save_img_local: bool = True
    ) -> Optional[PdfContent]:
        """非同步解析 PDF"""
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise PDFValidationError(f"PDF file not found: {pdf_path}")

        return await asyncio.to_thread(
            self._parse_pdf_sync, pdf_path, save_img_local=save_img_local
        )

    async def parse2pdf(self, pdf_path: Path) -> Optional[PdfContent]:
        """Parse PDF using Docling parser only.

        :param pdf_path: Path to PDF file
        :returns: PdfContent object or None if parsing failed
        """
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise PDFValidationError(f"PDF file not found: {pdf_path}")

        try:
            result = await self.docling_parser.parse_pdf(pdf_path)
            if result:
                logger.info(f"Parsed {pdf_path.name}")
                return result
            else:
                logger.error(f"Docling parsing returned no result for {pdf_path.name}")
                raise PDFParsingException(
                    f"Docling parsing returned no result for {pdf_path.name}"
                )

        except (PDFValidationError, PDFParsingException):
            raise
        except Exception as e:
            logger.error(f"Docling parsing error for {pdf_path.name}: {e}")
            raise PDFParsingException(f"Docling parsing error for {pdf_path.name}: {e}")
