from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from agents.multimodal_assistant import handle_multimodal_input
from agents.reasoning_agent import process_task
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from api.routes import dashboard



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI()
Instrumentator().instrument(app).expose(app)

origins = [
    "http://localhost",
    "http://localhost:5173",  # 如果前端跑在 5173 port
    # 其他允許的來源
]


# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routers

app.include_router(dashboard.router,  tags=["dashboard"])












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