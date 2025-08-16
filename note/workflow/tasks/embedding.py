from prefect import task
from services.embedding import get_embedding

@task
def embed_text(text: str):
    return get_embedding(text)
