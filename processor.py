import os
import pytesseract
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import tempfile
from typing import Generator, Dict, Any, Union

class DocumentProcessor:
    """
    A class to process PDF documents, extracting text using either direct extraction (PyPDF2)
    or OCR (pytesseract) for scanned content.
    """

    def __init__(self, tesseract_cmd: str = None):
        """
        Initialize the DocumentProcessor.
        
        Args:
            tesseract_cmd (str, optional): Path to tesseract executable.
                                           If None, relies on PATH.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def _extract_text_from_page(self, page_obj) -> str:
        """
        Attempt to extract text directly from a PDF page object.
        """
        try:
            text = page_obj.extract_text()
            if text and len(text.strip()) > 50:  # Heuristic: if enough text is found
                return text.strip()
        except Exception:
            return ""
        return ""

    def _perform_ocr(self, image: Image.Image) -> str:
        """
        Perform OCR on a single image.
        """
        try:
            return pytesseract.image_to_string(image)
        except Exception as e:
            return f"[OCR Failed: {e}]"

    def process_pdf(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """
        Process a PDF file page by page.
        
        Args:
            file_path (str): Path to the PDF file.
            
        Yields:
            dict: Structured data for each page containing page number and text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Open PDF for reading
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)

                # We also need images for OCR if text extraction fails.
                # Converting entire PDF to images at once might be heavy for large files.
                # pdf2image allows treating PDF as images.
                # For page-by-page efficient handling with pdf2image, we usually convert chunks or single pages.
                
                for page_num in range(total_pages):
                    page_content = {
                        "page_number": page_num + 1,
                        "content": "",
                        "extraction_method": "text_extraction"
                    }

                    # 1. Try direct text extraction
                    page_obj = reader.pages[page_num]
                    extracted_text = self._extract_text_from_page(page_obj)

                    if extracted_text:
                        page_content["content"] = extracted_text
                    else:
                        # 2. Fallback to OCR
                        page_content["extraction_method"] = "ocr"
                        try:
                            # Convert specific page to image
                            images = convert_from_path(
                                file_path, 
                                first_page=page_num+1, 
                                last_page=page_num+1
                            )
                            if images:
                                ocr_text = self._perform_ocr(images[0])
                                page_content["content"] = ocr_text
                        except Exception as e:
                            page_content["error"] = str(e)

                    yield page_content

        except Exception as e:
            yield {"error": f"Failed to process PDF: {str(e)}"}
