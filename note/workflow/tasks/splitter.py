from prefect import task
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800, chunk_overlap=150, separators=["\n\n", "\n", "。", "，", " "]
)

@task
def split_text(text: str):
    return [c.strip() for c in splitter.split_text(text) if c.strip()]



# @task
# def split_text(md_text: str):
#     return splitter.split_text(md_text)