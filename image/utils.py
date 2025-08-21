import io
import os

import cv2
import numpy as np
from PIL import Image
from torchvision.models.segmentation import deeplabv3_resnet50
from ultralytics import YOLO

MODELS_DIR = os.getenv("MODELS_DIR", "/models")


# 載入 YOLOv8 (ultralytics)
def load_yolo(model_name="yolov8n.pt"):
    model_path = os.path.join(MODELS_DIR, model_name)
    if not os.path.exists(model_path):
        # 讓 ultralytics 自行下載小型模型
        return YOLO(model_name)
    return YOLO(model_path)


# 載入 DeepLabv3
def load_deeplab(device="cpu"):
    # 使用 torchvision pretrained weights
    model = deeplabv3_resnet50(pretrained=True, progress=False)
    model.to(device)
    model.eval()
    return model


# 圖像 read helper
def read_imagefile(file) -> Image.Image:
    image = Image.open(io.BytesIO(file)).convert("RGB")
    return image


# 將 PIL -> numpy (BGR) for opencv
def pil_to_bgr_np(img: Image.Image):
    arr = np.array(img)
    return arr[:, :, ::-1].copy()


# 產生 segmentation overlay
def segmentation_overlay(pil_img: Image.Image, mask: np.ndarray, alpha=0.6):
    # mask: HxW (class labels) -> 0 / >0 binary
    img = np.array(pil_img).astype(np.uint8)
    color_mask = np.zeros_like(img)
    # 使用單色 (綠)
    color_mask[mask > 0] = [0, 255, 0]
    overlay = cv2.addWeighted(img, 1 - alpha, color_mask, alpha, 0)
    return Image.fromarray(overlay)
