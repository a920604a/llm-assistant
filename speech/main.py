from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from prometheus_fastapi_instrumentator import Instrumentator


from faster_whisper import WhisperModel
from TTS.api import TTS

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


asr_model = WhisperModel("base", device="cpu")
tts_model = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False, gpu=False)

@app.post("/asr")
async def asr():
    segments, _ = asr_model.transcribe("sample.wav")
    text = " ".join([seg.text for seg in segments])
    return {"text": text}

@app.post("/tts")
async def tts():

    tts_model.tts_to_file(text="Hello world", file_path="out.wav")
    return {"audio_file": "out.wav"}