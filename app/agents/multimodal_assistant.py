from agents.vision_tools import describe_image, extract_ocr_text
from agents.speech_tools import transcribe_audio

async def handle_multimodal_input(text=None, image=None, audio=None):
    task_params = {}

    if audio:
        text_from_audio = transcribe_audio(audio)
        task_params["text"] = text_from_audio

    if image:
        img_desc = describe_image(image)
        ocr_text = extract_ocr_text(image)
        task_params["image_desc"] = img_desc
        task_params["ocr_text"] = ocr_text

    if text:
        task_params["text"] = text

    return task_params