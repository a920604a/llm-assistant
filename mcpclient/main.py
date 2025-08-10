from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from .utils import read_imagefile, load_yolo, load_deeplab, pil_to_bgr_np, segmentation_overlay
import numpy as np
import uuid



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI(title='MCP Client Service')

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

