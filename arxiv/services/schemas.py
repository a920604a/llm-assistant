# services/schemas.py
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParserType(str, Enum):
    """PDF parser types."""

    DOCLING = "docling"


class ArxivPaper(BaseModel):
    """Schema for arXiv API response data."""

    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: str
    updated_date: str
    pdf_url: Optional[str] = None


class ArxivMetadata(BaseModel):
    """Paper metadata from arXiv API."""

    title: str = Field(..., description="Paper title from arXiv")
    authors: List[str] = Field(..., description="Authors from arXiv")
    abstract: str = Field(..., description="Abstract from arXiv")
    arxiv_id: str = Field(..., description="arXiv identifier")
    categories: List[str] = Field(default_factory=list, description="arXiv categories")
    published_date: str = Field(..., description="Publication date")
    pdf_url: str = Field(..., description="PDF download URL")


class PaperSection(BaseModel):
    """Represents a section of a paper."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    level: int = Field(default=1, description="Section hierarchy level")


class PaperFigure(BaseModel):
    """Represents a figure in a paper."""

    caption: str = Field(..., description="Figure caption")
    id: str = Field(..., description="Figure identifier")


class PaperTable(BaseModel):
    """Represents a table in a paper."""

    caption: str = Field(..., description="Table caption")
    id: str = Field(..., description="Table identifier")


class PdfContent(BaseModel):
    """PDF-specific content extracted by parsers like Docling."""

    sections: List[PaperSection] = Field(
        default_factory=list, description="Paper sections"
    )
    figures: List[PaperFigure] = Field(default_factory=list, description="Figures")
    tables: List[PaperTable] = Field(default_factory=list, description="Tables")
    raw_text: str = Field(..., description="Full extracted text")
    references: List[str] = Field(default_factory=list, description="References")
    parser_used: ParserType = Field(..., description="Parser used for extraction")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Parser metadata"
    )


class ParsedPaper(BaseModel):
    """Complete paper data combining arXiv metadata and PDF content."""

    arxiv_metadata: ArxivMetadata = Field(..., description="Metadata from arXiv API")
    pdf_content: Optional[PdfContent] = Field(
        None, description="Content extracted from PDF"
    )


class PaperBase(BaseModel):
    # Core arXiv metadata
    arxiv_id: str = Field(..., description="arXiv paper ID")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of author names")
    abstract: str = Field(..., description="Paper abstract")
    categories: List[str] = Field(..., description="Paper categories")
    published_date: datetime = Field(..., description="Date published on arXiv")
    pdf_url: str = Field(..., description="URL to PDF")


class PaperCreate(PaperBase):
    """Schema for creating a paper with optional parsed content."""

    # Parsed PDF content (optional - added when PDF is processed)
    raw_text: Optional[str] = Field(
        None, description="Full raw text extracted from PDF"
    )
    sections: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of sections with titles and content"
    )
    references: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of references if extracted"
    )

    # PDF processing metadata (optional)
    parser_used: Optional[str] = Field(
        None, description="Which parser was used (DOCLING, etc.)"
    )
    parser_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional parser metadata"
    )
    pdf_processed: Optional[bool] = Field(
        False, description="Whether PDF was successfully processed"
    )
    pdf_processing_date: Optional[datetime] = Field(
        None, description="When PDF was processed"
    )
