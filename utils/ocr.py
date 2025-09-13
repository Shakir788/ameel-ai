"""Simple OCR helper using pytesseract (requires tesseract installed on machine)"""
from PIL import Image
import pytesseract
import io

def ocr_image_bytes(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img, lang='eng+ara')  # arabic+english if available
    return text
