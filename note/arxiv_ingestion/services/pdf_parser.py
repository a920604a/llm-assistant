import logging
import asyncio
from pathlib import Path
from typing import Optional
import pdfplumber
import fitz  # PyMuPDF
import io
from PIL import Image
import os
from config import PDF_CACHE_DIR, MINIO_BUCKET
from db.minio import s3_client
from services.schemas import PdfContent, PaperSection, PaperTable, PaperFigure, ParserType
from typing import List


logger = logging.getLogger(__name__)
class TextExtractor:
    def extract(self, pdf_path: Path) -> (List[PaperSection], List[str]):
        sections, all_text = [], []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    sections.append(PaperSection(title=f"Page {i}", content=text, level=1))
                    all_text.append(text)
        return sections, all_text
    
    def extract_stream(self, pdf_stream: io.BytesIO) -> (List[PaperSection], List[str]):
        sections, all_text = [], []
        # pdfplumber 可以吃 BytesIO，不一定要檔案路徑
        with pdfplumber.open(pdf_stream) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    sections.append(PaperSection(title=f"Page {i}", content=text, level=1))
                    all_text.append(text)
        return sections, all_text



class TableExtractor:
    def extract(self, pdf_path: Path, pdf_filename: str) -> List[PaperTable]:
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                for t_idx, _ in enumerate(page_tables, start=1):
                    tables.append(PaperTable(
                        caption=f"Page {i} Table {t_idx}",
                        id=f"{pdf_filename}-p{i}-t{t_idx}"
                    ))
        return tables



class FigureExtractor:
    def __init__(self, image_dir: str = "./data/arxiv_images"):
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, pdf_path: Path, pdf_filename: str) -> List[PaperFigure]:
        figures = []
        pdf_document = fitz.open(pdf_path)
        for page_idx in range(len(pdf_document)):
            page = pdf_document.load_page(page_idx)
            for img_idx, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # object name (for MinIO and local)
                object_name = f"{pdf_filename}/p{page_idx+1}-img{img_idx}.{image_ext}"
                image_path = self.image_dir / object_name
                image_path.parent.mkdir(parents=True, exist_ok=True)

                pil_image = Image.open(io.BytesIO(image_bytes))

                # 本地存檔
                pil_image.save(image_path)

                # MinIO 上傳
                buffer = io.BytesIO()
                pil_image.save(buffer, format=pil_image.format or image_ext.upper())
                buffer.seek(0)
                s3_client.upload_fileobj(buffer, MINIO_BUCKET, object_name)

                # metadata
                figures.append(PaperFigure(
                    caption=f"Page {page_idx+1} Image {img_idx}",
                    id=f"s3://{MINIO_BUCKET}/{object_name}"
                ))
        pdf_document.close()
        return figures


# --------------------------
# Service Orchestrator
# --------------------------

class PDFParserService:
    """PDF 解析服務：抽文字、表格與圖片"""

    def __init__(self, 
                cache_dir: str = PDF_CACHE_DIR, 
                image_dir: str = "./data/arxiv_images"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.figure_extractor = FigureExtractor(image_dir=image_dir)

    def _parse_pdf_sync(self, pdf_path: Path) -> Optional[PdfContent]:
        pdf_path = Path(pdf_path)
        pdf_filename = pdf_path.stem

        if not pdf_path.exists():
            logger.warning(f"PDF file not found: {pdf_path}")
            return None

        try:
            # 抽取
            sections, all_text = self.text_extractor.extract(pdf_path)
            tables = self.table_extractor.extract(pdf_path, pdf_filename)
            figures = self.figure_extractor.extract(pdf_path, pdf_filename)

            return PdfContent(
                sections=sections,
                tables=tables,
                figures=figures,
                raw_text="\n".join(all_text),
                references=[],
                parser_used=ParserType.DOCLING,
                metadata={"pages": len(sections)}
            )

        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}", exc_info=True)
            return None

    async def parse_pdf(self, pdf_path: Path) -> Optional[PdfContent]:
        """非同步解析 PDF"""
        return await asyncio.to_thread(self._parse_pdf_sync, pdf_path)

