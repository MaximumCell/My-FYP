import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import tempfile
from typing import List, Dict


def ocr_image(image: Image.Image) -> str:
    """Run OCR on a PIL Image and return extracted text."""
    text = pytesseract.image_to_string(image, lang='eng')
    return text


def ocr_pdf(path: str) -> Dict:
    """Convert PDF to images and run OCR on each page.

    Returns a dict with per-page text and combined text.
    """
    result = {
        'pages': [],
        'text': ''
    }
    # convert_from_path may throw if poppler not installed — caller should handle
    images = convert_from_path(path)
    texts: List[str] = []
    for i, img in enumerate(images):
        page_text = ocr_image(img)
        result['pages'].append({'page': i + 1, 'text': page_text})
        texts.append(page_text)

    result['text'] = '\n\n'.join(texts)
    return result


def ocr_file(path: str) -> Dict:
    """Dispatch based on file extension. Supports PDF and common image types."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return ocr_pdf(path)
    else:
        # Try to open with PIL
        img = Image.open(path)
        text = ocr_image(img)
        return {'pages': [{'page': 1, 'text': text}], 'text': text}
