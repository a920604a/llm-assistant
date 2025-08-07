from fastapi import FastAPI, UploadFile, File, Form
from agents.multimodal_assistant import handle_multimodal_input
from agents.reasoning_agent import process_task
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI()

@app.post("/query")
async def query(text: str = Form(None), image: UploadFile = File(None), audio: UploadFile = File(None)):
    logger.info(f"Received query with text: {text}")
    image_bytes = await image.read() if image else None
    audio_bytes = await audio.read() if audio else None

    # 多模態助手 → 統一解析
    task_params = await handle_multimodal_input(text=text, image=image_bytes, audio=audio_bytes)
    logger.info(f"Parsed task parameters: {task_params}")

    # 主邏輯推理 Agent
    response = await process_task(task_params)
    return {"response": response}