from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from utils import read_imagefile, load_yolo, load_deeplab, pil_to_bgr_np, segmentation_overlay
import numpy as np
import uuid



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI(title='Multi-arch Vision Service')

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



# 全域載入模型（啟動時）
YOLO_MODEL = load_yolo('yolov8n.pt')
DEEPLAB = load_deeplab(device='cpu')

OUT_DIR = '/tmp/out'
os.makedirs(OUT_DIR, exist_ok=True)

@app.post('/detect')
async def detect(file: UploadFile = File(...)):
    content = await file.read()
    img = read_imagefile(content)
    # ultralytics 直接 accept PIL
    results = YOLO_MODEL.predict(img, imgsz=640, conf=0.25)
    # 取第一張結果
    r = results[0]
    boxes = []
    for box in r.boxes:
        b = box.xyxy[0].cpu().numpy().tolist()
        conf = float(box.conf[0].cpu().numpy())
        cls = int(box.cls[0].cpu().numpy())
        boxes.append({'xyxy': b, 'conf': conf, 'class': cls})
    # 儲存帶框圖
    vis = r.plot()
    out_path = os.path.join(OUT_DIR, f"detect_{uuid.uuid4().hex}.jpg")
    vis.save(out_path)
    return JSONResponse({'boxes': boxes, 'image': out_path})

@app.post('/segment')
async def segment(file: UploadFile = File(...)):
    content = await file.read()
    pil = read_imagefile(content)
    # preprocess
    transform = __import__('torch').nn.Identity()
    import torchvision.transforms as T
    tr = T.Compose([T.ToTensor(), T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])])
    input_tensor = tr(pil).unsqueeze(0)
    with __import__('torch').no_grad():
        out = DEEPLAB(input_tensor)['out'][0]
        pred = out.argmax(0).byte().cpu().numpy()
    overlay = segmentation_overlay(pil, pred)
    out_path = os.path.join(OUT_DIR, f"seg_{uuid.uuid4().hex}.jpg")
    overlay.save(out_path)
    return JSONResponse({'mask_image': out_path})