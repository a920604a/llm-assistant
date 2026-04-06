# 專案分析報告與改進建議

> 分析日期：2026-04-07

---

## 專案概述

這是一個**個人 arXiv 知識檢索平台**，核心功能包括：
- 自動化 arXiv 論文攝取（每日 Prefect 工作流）
- RAG 驅動的問答聊天（混合搜索 + 重排序）
- 電子郵件訂閱摘要服務
- 個人筆記 / 知識庫
- 全面的監控與可觀測性

**技術棧：** FastAPI · LangChain · Ollama · Qdrant · PostgreSQL · MinIO · Redis · Prefect · React + Firebase · Prometheus + Grafana + Langfuse

---

## 嚴重問題（Critical Issues）

### 1. 配置 Typo

| 檔案 | 錯誤 | 正確 |
|------|------|------|
| `apiGateway/config.py:18` | `FIRBASE_KEY_PATH` | `FIREBASE_KEY_PATH` |
| `.env.sample` | `DATABASE_UR` | `DATABASE_URL` |

### 2. CORS Origins 硬編碼

**位置：** `note/main.py:58`

```python
# 現狀（不應如此）
origins = ["http://apiGateway:8000", "http://localhost:7861"]
```

無法在不同環境中配置，存在安全風險。應移入 `.env`：

```python
# 建議做法
CORS_ORIGINS: list[str] = ["http://apiGateway:8000"]
```

### 3. 外部服務無重試機制

Ollama（300s timeout）、Qdrant、PostgreSQL 的 HTTP 調用均無重試邏輯，失敗時靜默無告警。

**建議：** 使用 `tenacity` 包裝關鍵外部調用：

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def call_ollama(...):
    ...
```

### 4. Prefect 流程無冪等性 / 回滾機制

`arxiv/arxiv_pipeline.py` 若在 embedding 步驟失敗，PostgreSQL 中已存入的論文元數據成為孤立記錄（無對應向量）。

**建議：** 為每篇論文在資料庫中添加 `processing_status` 欄位（`pending / indexed / failed`），支持安全重跑。

---

## 架構問題

### 5. 配置重複

`apiGateway/config.py` 和 `note/config.py` 各自定義了 `LangfuseSettings`、`MinioSettings` 等相同結構。

**建議：** 抽取為 `common/config.py` 共享模塊，各服務 import 使用。

### 6. 服務緊耦合

apiGateway 直接 HTTP 代理到 noteserver (`NOTE_API_URL`)，noteserver 地址變更即破壞。

**建議（按優先級）：**
1. 短期：將 URL 完全外部化到 `.env`
2. 長期：引入服務發現（Consul）或異步消息隊列（Celery + Redis）

### 7. 同步 I/O 在異步上下文

`note/main.py:57` 使用 `run_in_threadpool` 包裹本應異步的操作。

**建議：** 使用 `qdrant-client` 的 async client（`AsyncQdrantClient`），`aiofiles` 處理檔案 I/O。

### 8. Redis TTL 硬編碼

`note/config.py` 中 `ttl_hour = 6` 無法通過環境變數配置，也無緩存清除策略。

---

## 安全問題

### 9. 輸入驗證不足

- 用戶查詢未驗證長度限制、特殊字元
- SlowAPI Rate limiting 配置不明確，可能未對單一用戶 ID 生效

**建議：**

```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    chat_id: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$')
```

### 10. Firebase Token 驗證覆蓋率

需確認 apiGateway 的所有業務路由（非 `/ping`）均有 Firebase token 驗證依賴注入。

---

## 可觀測性缺口

### 11. Langfuse 未全面整合

`apiGateway` 初始化了 Langfuse tracer 但未在所有路由中使用。

**建議：** 添加 FastAPI middleware 自動追蹤所有請求，或至少確保 `query`、`chat` 路由有完整 span 記錄。

### 12. 結構化日誌缺失

使用 Loguru 但缺少 JSON 格式化輸出，不利於日誌聚合（如 Loki）。

**建議：**

```python
logger.add(sys.stdout, format="{time} {level} {message}", serialize=True)
```

---

## 測試覆蓋率

`note/tests/` 目前只有 `test_ollama_client.py`，缺少：

- RAG 管道單元測試（embedding、hybrid search、re-ranking）
- E2E 整合測試（攝取 → 檢索 → LLM 回應 → 源引用）
- apiGateway 路由測試（auth、proxy、error handling）

**建議：** 優先補充 `note/tests/test_rag_pipeline.py` 使用 Qdrant 測試集群（或 in-memory mode）。

---

## 改進優先級

### 高優先級（立即修復）

| # | 項目 | 影響 |
|---|------|------|
| 1 | 修復 `FIRBASE_KEY_PATH`、`DATABASE_UR` typo | 可能導致啟動失敗 |
| 2 | CORS origins 外部化 | 安全 + 部署靈活性 |
| 3 | 外部服務添加重試（`tenacity`） | 可靠性 |
| 4 | 輸入驗證（Pydantic validators） | 安全性 |

### 中優先級（短期規劃）

| # | 項目 | 影響 |
|---|------|------|
| 5 | 共享配置模塊 `common/config.py` | 維護性 |
| 6 | Prefect 冪等性（`processing_status`） | 資料一致性 |
| 7 | 擴展測試覆蓋（E2E + 單元） | 可信度 |
| 8 | Langfuse 全鏈路追蹤中間件 | 可觀測性 |

### 低優先級（長期優化）

| # | 項目 | 影響 |
|---|------|------|
| 9 | API 版本化（`/api/v2/`） | 未來相容性 |
| 10 | 聊天歷史歸檔 / 清理策略 | 儲存成本 |
| 11 | 進階 RAG：查詢擴展、子問題分解 | 檢索品質 |
| 12 | CI/CD（GitHub Actions） | 開發效率 |

---

## 優點總結

- **模塊化架構清晰**：gateway / noteserver / arxiv / email 職責分離明確
- **混合搜索設計良好**：dense embedding + BM25，RRF fusion 結合效果佳
- **監控工具齊全**：Prometheus + Grafana + Langfuse + AlertManager
- **多語言支持**：自動翻譯回應為用戶語言
- **Docker Compose 多環境配置完善**：dev / gpu / monitor / obs / storage 分層清晰
