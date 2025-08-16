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

 
from fetch_data import fetch_documents

from workflow.tasks.metadata import generate_metadata
from workflow.tasks.splitter import split_text
from workflow.tasks.embedding import embed_text
from workflow.tasks.qdrant_ops import upload_points


from logger import get_logger

logger = get_logger(__name__)

@flow(name="Import Markdown Notes")
def ingest_notes_pipeline(documents: List[Dict[str, Any]]):
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

    metadata = generate_metadata.submit(course + section + text + question).result()

    chunks = split_text.submit(text).result()
    for chunk in chunks:
        vector = embed_text.submit(chunk).result()
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

    upload_points(points)



# {'text': "Yes, even if you don't register, you're still eligible to submit the homeworks.\nBe aware, however, that there will be deadlines for turning in the final projects. So don't leave everything for the last minute.",
#  'section': 'General course-related questions',
#  'question': 'Course - Can I still join the course after the start date?',
#  'course': 'data-engineering-zoomcamp'}

def cli():

    documents = fetch_documents()

    ingest_notes_pipeline(documents)

if __name__ == "__main__":
    cli()