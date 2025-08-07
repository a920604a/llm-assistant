import glob
import os
import json
import click
import requests
from typing import List
from prefect import flow, task
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient, models 
from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
import re

# === 基本設定 ===
OLLAMA_API_URL = "http://ollama:11434"
QDRANT_URL = "http://qdrant:6333"
collection_name = "notes_collection"

# === LangChain ===
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", "。", "，", " "]
)



def get_embedding(text: str, use_sentence_transformers: bool = True) -> List[float]:
    if use_sentence_transformers: # 輸出向量維度是 768。
        model_name = 'uer/sbert-base-chinese-nli'
        model = SentenceTransformer(model_name)
        vector = model.encode([text])  # 仍需包成 list 傳入
        return vector[0].tolist()      # 取第一筆並轉 list[float]
    else:
        model_name = "BAAI/bge-small-zh-v1.5"
        embedder = TextEmbedding(model_name=model_name)
        return next(embedder.embed([text]))  # generator 中取出第一筆
    
    
# === Qdrant 初始化 ===
qdrant_client = QdrantClient(host="qdrant", port=6333)

# ✅ 建立 Collection（若尚未建立）
@task
def ensure_qdrant_collection():
    if collection_name not in [c.name for c in qdrant_client.get_collections().collections]:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )


# ✅ 翻譯文字
@task
def ollama_translate(text: str, model: str = "gpt-oss:20b") -> str:
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": model,
            "prompt": f"請幫我將以下內容翻譯成繁體中文：\n{text}",
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["response"]


def clean_json_string(s: str) -> str:
    # 移除開頭的 ```json 與結尾的 ```
    s = s.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s
# ✅ 產出 Metadata
@task
def ollama_generate_metadata(text: str, model: str = "gpt-oss:20b") -> dict:
    meta_prompt = f"""
請閱讀以下教學筆記，並分析出以下屬性：
- 主題分類（以一段文字描述）
- 適合程度（初學者、中階、進階）
- 三個關鍵字

教學內容如下：
{text}
請用 JSON 格式輸出，例如：
{{
  "title": "大數據架構設計",
  "level": "中階",
  "keywords": ["數據轉型", "分散式儲存", "資料湖"]
}}
"""
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={
            "model": model,
            "prompt": meta_prompt,
            "stream": False,
        },
    )
    response.raise_for_status()
    raw = response.json()["response"]
    try:
        cleaned = clean_json_string(raw)
        return json.loads(cleaned)
    except Exception:
        print("⚠️ 無法解析 metadata JSON，回傳為：", raw)
        return {"topic": "", "level": "", "keywords": []}


# ✅ 主流程：匯入筆記
@flow(name="Import Markdown Notes")
def import_md_notes_flow(md_text_dict: dict):
    ensure_qdrant_collection()

    points = []
    idx = 0
    BATCH_SIZE = 1

    for filename, md_text in md_text_dict.items():
        print(f"➡️ 處理檔案：{filename}，原始字數: {len(md_text)}")
        translated = ollama_translate(md_text)
        # print(f"翻譯結果 : {translated}")

        print("🧠 產出 Metadata...")
        metadata = ollama_generate_metadata(translated)
        print(f"Metadata 結果 : {metadata}")

        print("✂️ 分段中...")
        chunks = text_splitter.split_text(translated)
        for chunk in chunks:
            # vector = embeddings.embed_query(chunk)
            vector = get_embedding(chunk)
            # print(vector.shape())
            payload = {
                "text": chunk,
                "translated": True,
                **metadata,
            }
            points.append(
                models.PointStruct(id=idx, vector=vector, payload=payload)
            )
            idx += 1
            if len(points) >= BATCH_SIZE:
                qdrant_client.upsert(collection_name=collection_name, points=points)
                print(f"寫入 {len(points)} 筆資料")
                points = []  # 清空已寫入的 batch
            
    # 寫入最後剩餘的點
    if points:
        qdrant_client.upsert(collection_name=collection_name, points=points)
        print(f"寫入最後 {len(points)} 筆資料")
    # print(f"📦 寫入 {len(points)} 筆資料到 Qdrant")
    # qdrant_client.upsert(collection_name=collection_name, points=points)


# ✅ CLI 介面使用 click
@click.command()
@click.option('--folder', type=click.Path(exists=True, file_okay=False), required=True, help='Markdown 資料夾路徑')
def cli(folder):
    # 找資料夾內所有 .md 檔案路徑
    md_files = glob.glob(os.path.join(folder, '*.md'))
    all_texts = {}
    for file in md_files:
        with open(file, 'r', encoding='utf-8') as f:
            # all_texts.append(f.read())
            all_texts[file] = f.read()
    import_md_notes_flow(all_texts)

if __name__ == "__main__":
    cli()
# python ingest.py --file /ingest/'Chapter 1_ Big Data.md'