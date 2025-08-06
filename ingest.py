import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import os

# ✅ 設定 API 金鑰與服務端點
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
OLLAMA_API_URL = "http://localhost:11434"

# ✅ 基本設定
collection_name = "notes_collection"

# ✅ Langchain 設定
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
embeddings = OpenAIEmbeddings()

# ✅ Qdrant 初始化
qdrant_client = QdrantClient(url="http://localhost:6333")

if collection_name not in [c.name for c in qdrant_client.get_collections().collections]:
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=1536, distance=rest.Distance.COSINE),
    )


# ✅ 翻譯文字
def ollama_translate(text: str) -> str:
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": "llama3",  # 或您有自己命名的翻譯模型
            "prompt": f"請幫我將以下內容翻譯成繁體中文：\n{text}",
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["response"]


# ✅ 產出教學筆記的 Metadata
def ollama_generate_metadata(text: str) -> dict:
    meta_prompt = f"""
請閱讀以下教學筆記，並分析出以下屬性：
- 主題分類（以一段文字描述）
- 適合程度（初學者、中階、進階）
- 三個關鍵字

教學內容如下：
{text}
請用 JSON 格式輸出，例如：
{{
  "topic": "大數據架構設計",
  "level": "中階",
  "keywords": ["數據轉型", "分散式儲存", "資料湖"]
}}
"""
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": "llama3",
            "prompt": meta_prompt,
            "stream": False,
        },
    )
    response.raise_for_status()
    raw = response.json()["response"]

    # 嘗試解析 JSON
    try:
        import json
        return json.loads(raw)
    except Exception:
        print("⚠️ 無法解析 metadata JSON，回傳為：", raw)
        return {"topic": "", "level": "", "keywords": []}


# ✅ 匯入 Markdown 筆記（自動翻譯 + Metadata + 切割 + 寫入 Qdrant）
def import_md_notes(md_text_list):
    points = []
    idx = 0

    for md_text in md_text_list:
        print(f"➡️ 翻譯中（原始字數: {len(md_text)}）...")
        translated = ollama_translate(md_text)

        print("🧠 產出 Metadata...")
        metadata = ollama_generate_metadata(translated)

        print("✂️ 分段中...")
        chunks = text_splitter.split_text(translated)
        for chunk in chunks:
            vector = embeddings.embed_query(chunk)
            payload = {
                "text": chunk,
                "translated": True,
                **metadata,
            }
            points.append(
                rest.PointStruct(id=idx, vector=vector, payload=payload)
            )
            idx += 1

    print(f"📦 寫入 {len(points)} 筆資料到 Qdrant")
    qdrant_client.upsert(collection_name=collection_name, points=points)


# ✅ 測試匯入範例
# md_notes = [
#     """
# # Chapter 1: Big Data
# To do that, you need a data architecture to ingest, store, transform, and model the data so it can be accurately and easily used.
# ## What Is Big Data?
# Big Data is defined by Volume, Variety, Velocity...
# """
# ]

import_md_notes(md_notes)
