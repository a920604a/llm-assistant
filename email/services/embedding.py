from typing import List

from sentence_transformers import SentenceTransformer

# 先載入模型
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def get_embedding(text: str) -> List[float]:
    """
    將文字轉成向量 (384 維)
    """
    vector = model.encode([text])
    return vector[0].tolist()
