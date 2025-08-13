from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from api.routers import query


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI()
Instrumentator().instrument(app).expose(app)

origins = ["http://mcpclient:8000"]


# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routers

app.include_router(query.router, tags=["query"])
