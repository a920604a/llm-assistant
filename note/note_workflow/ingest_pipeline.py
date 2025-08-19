import glob
import os
import click
import jieba
from tqdm.auto import tqdm
from qdrant_client import models

from logger import get_logger
from prefect import flow

from note_workflow.tasks.translator import ollama_translate
from note_workflow.tasks.metadata import ollama_generate_metadata
from note_workflow.tasks.splitter import split_text
from note_workflow.tasks.embedding import embed_text
from note_workflow.tasks.qdrant_ops import upload_points

logger = get_logger(__name__)


# ✅ 主流程：匯入筆記
@flow(name="Import Markdown Notes")
def ingest_notes_pipeline(md_text_dict: dict):

    points = []
    idx = 0

    for filename, md_text in tqdm(
        md_text_dict.items(), total=len(md_text_dict), desc="處理檔案"
    ):
        logger.info(f"➡️ 處理檔案：{filename}，字數: {len(md_text)}")
        translated = ollama_translate.submit(md_text).result()
        translated = md_text

        metadata = ollama_generate_metadata.submit(translated).result()
        chunks = split_text.submit(translated).result()

        for chunk in chunks:
            vector = embed_text.submit(chunk).result()
            bm25_text = " ".join(jieba.cut(chunk))
            payload = {
                "text": chunk,
                "bm25_text": bm25_text,
                "translated": True,
                **metadata,
            }
            points.append(models.PointStruct(id=idx, vector=vector, payload=payload))
            idx += 1

    upload_points(points)


# ✅ CLI 介面使用 click
@click.command()
@click.option(
    "--file",
    "path",  # 把 CLI 的 --file 對應到變數 path
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
    help="Markdown 檔案或資料夾路徑",
)
def cli(path):
    all_texts = {}

    if os.path.isdir(path):
        # 找資料夾內所有 .md 檔案路徑
        md_files = glob.glob(os.path.join(path, "*.md"))
        for file in md_files:
            with open(file, "r", encoding="utf-8") as f:
                all_texts[file] = f.read()

    elif os.path.isfile(path) and path.endswith(".md"):
        # 單一 .md 檔案
        with open(path, "r", encoding="utf-8") as f:
            all_texts[path] = f.read()

    else:
        click.echo("請提供 .md 檔案或包含 .md 檔案的資料夾", err=True)
        return

    ingest_notes_pipeline(all_texts)


if __name__ == "__main__":
    cli()
# python ingest.py --file /ingest/'Chapter 1_ Big Data.md'
