import glob
import os
import json
import click
import re
import requests
import jieba
from typing import List, Dict, Any
from tqdm.auto import tqdm
from prefect import flow, task
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import models

from storage.qdrant import qdrant_client
from conf import OLLAMA_API_URL, COLLECTION_NAME
from services.embedding import get_embedding
from conf import MODEL_NAME
from fetch_data import fetch_documents
from logger import get_logger

logger = get_logger(__name__)

# === LangChain ===
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800, chunk_overlap=150, separators=["\n\n", "\n", "。", "，", " "]
)


# ✅ 產出 Metadata
@task
def ollama_generate_metadata(text: str, model: str = MODEL_NAME) -> dict:
    meta_prompt = f"""
Please read the following tutorial notes and analyze the following attributes:

Topic classification (describe in one paragraph)

Suitable level (Beginner, Intermediate, Advanced)

Three keywords

The tutorial content is as follows:
{text}

Please output in JSON format, for example:

{{
  "title": "Big Data Architecture Design",
  "level": "Intermediate",
  "keywords": ["Data Transformation", "Distributed Storage", "Data Lake"]
}}

"""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": model,
                "prompt": meta_prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json().get("response", "")
        
        
        cleaned = clean_json_string(raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("⚠️ 無法解析 metadata JSON，回傳為：%s", raw)
            data = {}
            
        title = (
            data.get("title")
            or data.get("topic")
            or data.get("topic_classification")
            or ""
        )
        level = (
            data.get("level")
            or data.get("suitable_level")
            or ""
        )
        keywords = data.get("keywords")
        if not isinstance(keywords, list):
            if isinstance(keywords, str):
                keywords = [kw.strip() for kw in keywords.split(",") if kw.strip()]
            else:
                keywords = []

        # 保證三欄一定存在
        return {
            "title": title,
            "level": level,
            "keywords": keywords
        }
    except Exception as e:
        logger.info(f"⚠️ 取得/解析 metadata 失敗：{e}")
        return {"title": "", "level": "", "keywords": []}



def clean_json_string(s: str) -> str:
    # 移除開頭的 ```json 與結尾的 ```
    s = s.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s



@flow(name="Import Markdown Notes")
def import_md_notes_flow(documents: List[Dict[str, Any]]):
    points: List[models.PointStruct] = []
    idx = 0

    # for doc in tqdm(documents, total=min(len(documents), 1), desc="處理文件"):
    doc = documents[0]
    text = (doc.get("text") or "").strip()
    course = str(doc.get("course", "")).strip() or "unknown_course"
    section = str(doc.get("section", "")).strip() or "unknown_section"
    question = str(doc.get("question", "")).strip() or "unknown_question"
        
    # if not text:
    #     continue

    filename = f"{course}/{section}/{question}"
    
    logger.info(f"➡️ 處理檔案：{filename}，原始字數: {len(text)}")
    click.echo(f"➡️ 處理檔案：{filename}，原始字數: {len(text)}")

    translated = text
    logger.info(f"翻譯結果 : {translated[:200]}{'...' if len(translated) > 200 else ''}")
    click.echo(f"翻譯結果 : {translated[:200]}{'...' if len(translated) > 200 else ''}")

    logger.info("🧠 產出 Metadata...")
    metadata = ollama_generate_metadata(course + section + text + question)
    logger.info(f"Metadata 結果 : {metadata}")
    click.echo(f"Metadata 結果 : {metadata}")
    
    
    logger.info("✂️ 分段中...")
    click.echo("✂️ 分段中...")
    chunks = text_splitter.split_text(translated)


    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # vector = embeddings.embed_query(chunk)
        # 向量化 chunk
        vector = get_embedding(chunk)
        # logger.info(vector.shape())
        # 中文分詞作為 BM25 payload
        # bm25_text = " ".join(jieba.cut(chunk))
        payload = {
            "text": chunk,
            "translated": False,
            "course": course,
            "section": section,
            "question": question,
            **metadata,
        }
        
        points.append(models.PointStruct(id=idx, vector=vector, payload=payload))
        idx += 1

    # 上傳到 Qdrant
    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"✅ 已上傳 {len(points)} 個分段至 Qdrant（collection: {COLLECTION_NAME}）")
        click.echo(f"✅ 已上傳 {len(points)} 個分段至 Qdrant（collection: {COLLECTION_NAME}）")
    else:
        logger.info("⚠️ 無可上傳的分段（points 為空）")
        click.echo("⚠️ 無可上傳的分段（points 為空）")



# {'text': "Yes, even if you don't register, you're still eligible to submit the homeworks.\nBe aware, however, that there will be deadlines for turning in the final projects. So don't leave everything for the last minute.",
#  'section': 'General course-related questions',
#  'question': 'Course - Can I still join the course after the start date?',
#  'course': 'data-engineering-zoomcamp'}

def cli():

    documents = fetch_documents()

    import_md_notes_flow(documents)

if __name__ == "__main__":
    cli()