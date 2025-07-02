
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uvicorn

from agent.core_agent import handle_user_query  # 主處理邏輯

app = FastAPI()


# 輸入格式：可同時提供文字與圖片
class QueryInput(BaseModel):
    text: Optional[str] = None

@app.post("/query")
async def query_with_optional_image(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    image_bytes = await image.read() if image else None
    response = await handle_user_query(text=text, image=image_bytes)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)