from PIL import Image, ImageDraw, ImageFont
import os

from backend.ai.ocr_processor import ocr_image


def test_ocr_image_basic():
    # Create a small image with text
    img = Image.new('RGB', (200, 60), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        # Use a truetype font if available
        font = ImageFont.load_default()
    except Exception:
        font = None
    d.text((10, 10), "Test OCR", fill=(0, 0, 0), font=font)

    text = ocr_image(img)
    assert isinstance(text, str)
    # We may not get exact text depending on tesseract; ensure non-empty
    assert len(text.strip()) > 0
