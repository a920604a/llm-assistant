from typing import List
from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer


def get_embedding(text: str, use_sentence_transformers: bool = True) -> List[float]:
    if use_sentence_transformers:  # 輸出向量維度是 768，文本（論文摘要、段落）上表現更好
        # {"all-MiniLM-L6-v2":"384 維，速度快，效果佳，社群最常用。CHUNK_SIZE = 200~400 字 , overlap = 50~100",
        # "all-mpnet-base-v2","768 維，準確率更高，尤其在長文本（論文摘要、段落）上表現更好。CHUNK_SIZE = 400~600 字（約 500 token） , overlap = 50~100",
        # "multi-qa-mpnet-base-dot-v1":"768 維，專為 QA 與檢索任務設計，適合用來做「query → 找最相關論文」。CHUNK_SIZE = 400~600 字, overlap = 50~100",}
        model_name = "all-mpnet-base-v2"
        model = SentenceTransformer(model_name)
        vector = model.encode(text)  
        return vector.tolist()
    
