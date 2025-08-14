from typing import List
from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer


def get_embedding(text: str, use_sentence_transformers: bool = True) -> List[float]:
    if use_sentence_transformers:  # 輸出向量維度是 384
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        model = SentenceTransformer(model_name)
        vector = model.encode([text])  # 仍需包成 list 傳入
        return vector[0].tolist()  # 取第一筆並轉 list[float]
    else:
        model_name = "BAAI/bge-small-zh-v1.5"
        embedder = TextEmbedding(model_name=model_name)
        return next(embedder.embed([text]))  # generator 中取出第一筆
