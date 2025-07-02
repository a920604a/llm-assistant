from PIL import Image
import pytesseract
import io

# TODO: 可接 GPT-4o Vision 分析圖像內容

def describe_image(image_bytes):
    return "這看起來是一張 Minecraft 村莊的圖片。"

def extract_ocr_text(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)