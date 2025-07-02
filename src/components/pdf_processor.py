from abc import ABC, abstractmethod
from pathlib import Path
import logging
from typing import List
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io

from ..models.schemas import ExtractedFile, ExtractedPage

logger = logging.getLogger(__name__)


class BaseExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> ExtractedFile:
        raise NotImplementedError


class OCRExtractionStrategy(BaseExtractionStrategy):
    def extract(self, file_path: str) -> ExtractedFile:
        """Extract text from PDF using OCR (pytesseract and Pillow)"""
        logger.info(f"Extracting text from {file_path} using OCR")
        
        pages = []
        pdf_document = fitz.open(file_path)
        
        try:
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(2, 2)  # 2x scaling for better OCR quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.pil_tobytes(format="PNG")
                image = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                text = pytesseract.image_to_string(image, lang='pol')  # Polish language
                
                pages.append(ExtractedPage(
                    page_number=page_num + 1,
                    content=text
                ))
                
                logger.debug(f"Extracted page {page_num + 1} using OCR")
                
        finally:
            pdf_document.close()
        
        return ExtractedFile(
            filename=Path(file_path).name,
            extraction_method='ocr',
            pages=pages
        )


class TextLayerExtractionStrategy(BaseExtractionStrategy):
    def extract(self, file_path: str) -> ExtractedFile:
        """Extract text from PDF using text layer (PyMuPDF/fitz)"""
        logger.info(f"Extracting text from {file_path} using text layer")
        
        pages = []
        pdf_document = fitz.open(file_path)
        
        try:
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text()
                
                pages.append(ExtractedPage(
                    page_number=page_num + 1,
                    content=text
                ))
                
                logger.debug(f"Extracted page {page_num + 1} using text layer")
                
        finally:
            pdf_document.close()
        
        return ExtractedFile(
            filename=Path(file_path).name,
            extraction_method='text',
            pages=pages
        )


class PDFProcessor:
    """Factory class for PDF processing strategies"""
    
    def __init__(self):
        self.strategies = {
            'ocr': OCRExtractionStrategy(),
            'text': TextLayerExtractionStrategy()
        }
    
    def extract(self, file_path: str, method: str) -> ExtractedFile:
        """Extract text from PDF using specified method"""
        if method not in self.strategies:
            raise ValueError(f"Unknown extraction method: {method}")
        
        strategy = self.strategies[method]
        return strategy.extract(file_path)