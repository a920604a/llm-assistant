from typing import List
from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer

# Hugging Face 會自動把模型下載到 cache
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def get_embedding(text: str) -> List[float]:
    # 輸出向量維度是 384
    vector = model.encode([text])  # 仍需包成 list 傳入
    return vector[0].tolist()  # 取第一筆並轉 list[float]