## 前言


在 AI / LLM 應用中，最大的挑戰不是「能不能跑」，而是「為什麼結果會這樣」。
如果無法觀測，就無法優化。

Langfuse 就像是一副「觀測之眼」，能把每一次 LLM 的請求、延遲、Token 消耗到整個 RAG Pipeline 的流程完整記錄下來。這篇文章會示範如何把 Langfuse 用在 RAG Pipeline 中，並介紹實務封裝與 Self-host 架構設計，讓你能從黑箱中獲得清晰的運行視角。

## Langfuse 核心概念（Trace / Span / Generation / ID 關聯）

「萬物皆可追蹤」——在 AI / LLM 應用中，若你無法觀察，那就無法優化。
今天我們要把 Langfuse 當成魔法觀測鏡，記錄每一次 LLM 調用，每一段 prompt、token 使用、延遲、錯誤，通通攤在眼前。



在傳統後端系統中，我們會記 log、監控 CPU / memory、做 metrics（如響應時間、錯誤率）。但在 LLM 應用中，加入「語言模型呼叫」「prompt 選擇」「生成輸出」「cost / token 使用」等層次後，系統變成黑箱。
可觀測性不只是「有 log 就算了」——而是要 Trace / Span / Metrics / Alert / 深入關聯，才能真正找到瓶頸、診斷異常、優化模型。

Langfuse 正是為這類場景設計的觀測平台，它與 OpenTelemetry（OTel）兼容、提供 LLM 專用觀察（generation / span / trace）等觀測物件。

| 名稱                        | 角色 / 功能                  | 備註                                                                   |
| ------------------------- | ------------------------ | -------------------------------------------------------------------- |
| Trace                     | 一次完整操作流程（從入口到出口）         | 包含多個 Span / Generation；可跨服務 / 跨模組追蹤 ([Langfuse][1])                  |
| Span / Observation        | 單一操作單元                   | 如資料前處理、LLM 呼叫、資料庫查詢等，每個操作可成為一個 span ([Langfuse][2])                  |
| Generation                | 專屬 LLM 呼叫的 span 類型       | 帶有模型名稱、token 使用量、cost 等欄位 ([Langfuse][2])                            |
| Trace ID / Observation ID | 用來關聯 Trace / Span 的唯一識別碼 | 可以使用自己的 domain ID (如 correlationId) 或讓 Langfuse 自動產生 ([Langfuse][1]) |
| Session / Tags / Metadata | 對 Trace 做標籤、分類           | 幫助後續搜尋、分群、過濾                                                         |

[1]: https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing "Trace IDs & Distributed Tracing - Langfuse"
[2]: https://langfuse.com/docs/observability/sdk/python/overview "Overview of the Python SDK - Langfuse"


舉例：假設你有一個用戶請求觸發 LLM 回答，你可以為這個請求開一個 Trace，裡面包含：

1. 請求接收 / 驗證（span）
2. 資料檢索或 embedding 查詢（span）
3. LLM 呼叫（generation）
4. 輸出後處理（span）
5. 結果回傳（span）

這樣整條流程的每一環節都有可觀察性，若某一環延遲過高或 token 使用異常，就可以快速定位是哪一段出了問題。





### 🔍 Langfuse 開放式 LLM 工程平台

Langfuse 是一個開源的 LLM 工程平台，旨在幫助團隊協作開發、監控、評估和調試 AI 應用。它提供了全鏈路可觀察性、Prompt 管理、評測工具和數據集管理等功能，讓開發者能夠更高效地進行模型開發和優化。

🧩 Trace：記錄一次完整的 LLM 調用鏈

在 Langfuse 中，`Trace` 是記錄一次完整的 LLM 調用鏈的核心單位。它包含了用戶的 Prompt、系統的回應、調用的模型、生成的內容等信息，幫助開發者全面了解每一次模型調用的過程。


🧪 Span：細化每一步操作的追蹤

每個 Trace 可以包含多個 `Span`，用於細化記錄每一步操作的過程。例如，在一個多輪對話中，每一次模型的生成都可以作為一個 Span 進行記錄，幫助開發者分析每一步的行為。

📊 可視化界面：直觀展示模型行為

Langfuse 提供了直觀的可視化界面，開發者可以通過 Trace、Span、Session 等視圖，直觀地查看模型的行為和性能指標，幫助快速定位問題和進行優化。


🛠️ 集成與 SDK：靈活接入各種應用場景

Langfuse 提供了多種 SDK，包括 Python、JavaScript、OpenAI 等，支持與 LangChain、LlamaIndex、Litellm 等框架的集成，方便開發者在不同的應用場景中使用。


---

## 進階篇：完整 RAG Pipeline 追蹤

### 範例紀錄：我的追蹤詢問
- Trace ID：`abcd1234…`
- 使用者 user_id：`user_001`
- 流程路徑：embedding → retrieval → rerank → evaluation(可選) → prompt_span → LLM → 回傳


在 Langfuse 後台，我們能看到這次請求的完整樹狀結構（如下圖）：

![](https://github.com/a920604a/llm-assistant/blob/main/demo/langfuse_trace_span.png?raw=true)

對應到程式碼，整體流程如下：

```python
ask_flow

langfuse_tracer = LangfuseTracer(settings)
rag_tracer = RAGTracer(langfuse_tracer)

with rag_tracer.trace_request(request.user_id, ask_r.query) as trace:
    ├── embedding_span : get_embedding
    ├── search_span : search relevant chunks
    ├── rerank_span : re_rank
    ├── prompt_span : build prompt
    ├── gen_span    : generate response
rag_tracer.end_request(trace, response.answer, time.time() - start_time)
```

---

### 1️⃣ Embedding 生成

第一步是將 Query 轉換成向量：

```python
with rag_tracer.trace_embedding(trace, query=query) as embedding_span:
    query_embedding = get_embedding(query)
rag_tracer.end_embedding(embedding_span, query_embedding)
```

這裡的 `embedding_span` 記錄了輸入查詢與生成的向量，用於後續檢索。

---

### 2️⃣ 檢索相關文檔（Search）

接著進行向量與文本檢索：

```python
with rag_tracer.trace_search(trace, query=query, top_k=top_k, search_mode=search_mode) as search_span:
    chunks, sources, msg, arxiv_ids, total_hits = qdrant_client.search(
        query=query,
        query_vector=query_embedding,
        size=top_k * 2,
        min_score=0.3,
        hybrid=system_settings.hybrid_search,
        categories=categories,
    )
rag_tracer.end_search(search_span, chunks, arxiv_ids, total_hits)
```



---

### 3️⃣ 重排序（Re-ranking）

將檢索到的 chunks 根據相關性重新排序：

```python
with rag_tracer.trace_rerank(trace, query=query, vector_weight=vector_weight, bm25_weight=bm25_weight) as rerank_span:
    reranked = re_ranking(
        chunks,
        query,
        vector_weight=vector_weight,
        bm25_weight=bm25_weight,
    )
rag_tracer.end_rerank(rerank_span, reranked)
```

這一步的 `rerank_span` 幫助我們比較不同演算法（如 BM25 與向量檢索）的權重影響。

---

### 4️⃣ 建立 Prompt

根據排序後的 chunks 構建最終提示詞：

```python
with rag_tracer.trace_prompt_construction(trace, chunks) as prompt_span:
    prompt_data = ollama_client.prompt_builder.create_structured_prompt(query, chunks, system_settings.user_language)
    final_prompt = prompt_data["prompt"]
rag_tracer.end_prompt(prompt_span, final_prompt)
```

這裡的 `prompt_span` 不只記錄了原始 chunks，還能看到最終的 prompt 字串，用於後續的 LLM 呼叫。

---

### 5️⃣ 生成答案（LLM Generation）

最後，將 prompt 送入模型產生答案：

```python
with rag_tracer.trace_generation(trace, model, final_prompt) as gen_span:
    parsed_response, response = await ollama_client.generate_rag_answer(
        query=query,
        chunks=chunks,
        user_language=system_settings.user_language,
        use_structured_output=False,
        temperature=system_settings.temperature,
    )
    rag_tracer.end_generation(gen_span, response, model)
```

在這個 `gen_span` 裡，我們能觀測：

* 模型名稱（如 `gpt-oss:20b`）

---


## Self-host 架構說明

在自建（self-hosted）Langfuse 架構中，主要由兩大類服務與儲存系統組成：

1. **應用層（Application）**：負責接收、處理、顯示觀測資料
2. **儲存／資料層（Storage / Backend）**：承載 Trace / Span / 元資料 / Blob 儲存等

下面是官方 Self-hosting 文件中對架構的描述：

> Langfuse consists of two application containers (Web + Worker)、儲存組件（Postgres, ClickHouse, Redis / 缓存, S3 / Blob Storage）等。([Langfuse]( https://langfuse.com/self-hosting))

附錄的 `docker-compose` 配置映射這樣的組件：worker / web / PostgreSQL / ClickHouse / MinIO / Redis，並且共用一個網路 `langfuse-otel-net` 以利內部通訊。

---


![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*mBla5iLQvB86f-U5fPtANA.png)


以上流程對應的是：

1. Web/API 層接收來自 SDK / 客戶端的觀測事件 / 查詢
2. Web 儲存輕量 metadata 至 PostgreSQL + 暫存 / queue 至 Redis
3. 原始事件／大檔資料（如 JSON payload、multi-modal）先存 Blob / MinIO
4. Worker 拉取事件做解析 / 計算 / 拆解後寫入 ClickHouse
5. Web 查詢 UI 查詢時，主要從 ClickHouse 讀出結果，並整合 Postgres / Blob Content

---

### 各組件角色與責任


#### **langfuse-worker**

* 處理 ingestion queue 中的觀測事件（Trace / Span / Generation）
* 從 Blob / MinIO 讀出原始資料、做解析、補足欄位、轉寫至 ClickHouse
* 負責背景任務（batch 寫入、資料轉換、補發重試）
* 環境變數中設定 ClickHouse / Postgres / MinIO 參數，如 `CLICKHOUSE_URL`、`DATABASE_URL`、`LANGFUSE_S3_EVENT_UPLOAD_*` 等

#### **langfuse-web**

* 提供前端 UI（Trace 檢視、查詢視圖）與 API 入口
* 處理驗證、權限、用戶設定、prompt 管理等元資料邏輯
* 接收觀測事件請求，做初步快取 / 上傳 Blob，再排入 queue
* 初始化 Org / Project、Web 端管理功能

### **ClickHouse**

* 作為高效能的 OLAP 儲存，用於大量 Trace / Span / Observations 查詢
* 所有重度查詢 / 分析操作皆進行於此，避免污染主交易庫
* 在官方架構中是不可或缺的組件（自建 Langfuse 必須包含 ClickHouse）([Langfuse][4])

#### **PostgreSQL**

* 儲存元資料 / 配置 / 設定 / 使用者帳號 / API 金鑰等交易性資料
* Web 層與 Worker 層都會讀寫這部分資料

#### **MinIO（或 S3 相容）**

* 用來儲存原始事件 payload、Multi-modal 資料、文件、匯出檔案
* 確保即使資料庫不可用，也不丟失原始事件，待恢復再處理

#### **Redis**

* 作為快取 / 緩存層，用來快取 prompt / API key / 權限檢查等
* Queue 或中介層：Web 將事件放入 Redis / queue，Worker 從中取出
* 提高吞吐效率，降低對 Postgres / ClickHouse 的即時負擔

---

### docker compose
```

networks:
  langfuse-otel-net:
    external: true

services:
  langfuse-worker:
    image: docker.io/langfuse/langfuse-worker:3
    restart: always
    depends_on: &langfuse-depends-on
      langfuse-postgres:
        condition: service_healthy
      langfuse-minio:
        condition: service_healthy
      langfuse-redis:
        condition: service_healthy
      langfuse-clickhouse:
        condition: service_healthy
    ports:
      - 127.0.0.1:3030:3030
    environment: &langfuse-worker-env
      NEXTAUTH_URL: http://localhost:3000
      DATABASE_URL: postgresql://postgres:postgres@langfuse-postgres:5432/postgres # CHANGEME
      SALT: "mysalt" # CHANGEME
      ENCRYPTION_KEY: "0000000000000000000000000000000000000000000000000000000000000000" # CHANGEME: generate via `openssl rand -hex 32`
      TELEMETRY_ENABLED: ${TELEMETRY_ENABLED:-true}
      LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES: ${LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES:-true}
      CLICKHOUSE_MIGRATION_URL: ${CLICKHOUSE_MIGRATION_URL:-clickhouse://langfuse-clickhouse:9000}
      CLICKHOUSE_URL: ${CLICKHOUSE_URL:-http://langfuse-clickhouse:8123}
      CLICKHOUSE_USER: ${CLICKHOUSE_USER:-clickhouse}
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD:-clickhouse} # CHANGEME
      CLICKHOUSE_CLUSTER_ENABLED: ${CLICKHOUSE_CLUSTER_ENABLED:-false}
      LANGFUSE_USE_AZURE_BLOB: ${LANGFUSE_USE_AZURE_BLOB:-false}
      LANGFUSE_S3_EVENT_UPLOAD_BUCKET: ${LANGFUSE_S3_EVENT_UPLOAD_BUCKET:-langfuse}
      LANGFUSE_S3_EVENT_UPLOAD_REGION: ${LANGFUSE_S3_EVENT_UPLOAD_REGION:-auto}
      LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID: ${LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID:-minio}
      LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY: ${LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY:-miniosecret} # CHANGEME
      LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT: ${LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT:-http://langfuse-minio:9000}
      LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE: ${LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE:-true}
      LANGFUSE_S3_EVENT_UPLOAD_PREFIX: ${LANGFUSE_S3_EVENT_UPLOAD_PREFIX:-events/}
      LANGFUSE_S3_MEDIA_UPLOAD_BUCKET: ${LANGFUSE_S3_MEDIA_UPLOAD_BUCKET:-langfuse}
      LANGFUSE_S3_MEDIA_UPLOAD_REGION: ${LANGFUSE_S3_MEDIA_UPLOAD_REGION:-auto}
      LANGFUSE_S3_MEDIA_UPLOAD_ACCESS_KEY_ID: ${LANGFUSE_S3_MEDIA_UPLOAD_ACCESS_KEY_ID:-minio}
      LANGFUSE_S3_MEDIA_UPLOAD_SECRET_ACCESS_KEY: ${LANGFUSE_S3_MEDIA_UPLOAD_SECRET_ACCESS_KEY:-miniosecret} # CHANGEME
      LANGFUSE_S3_MEDIA_UPLOAD_ENDPOINT: ${LANGFUSE_S3_MEDIA_UPLOAD_ENDPOINT:-http://localhost:9091}
      LANGFUSE_S3_MEDIA_UPLOAD_FORCE_PATH_STYLE: ${LANGFUSE_S3_MEDIA_UPLOAD_FORCE_PATH_STYLE:-true}
      LANGFUSE_S3_MEDIA_UPLOAD_PREFIX: ${LANGFUSE_S3_MEDIA_UPLOAD_PREFIX:-media/}
      LANGFUSE_S3_BATCH_EXPORT_ENABLED: ${LANGFUSE_S3_BATCH_EXPORT_ENABLED:-false}
      LANGFUSE_S3_BATCH_EXPORT_BUCKET: ${LANGFUSE_S3_BATCH_EXPORT_BUCKET:-langfuse}
      LANGFUSE_S3_BATCH_EXPORT_PREFIX: ${LANGFUSE_S3_BATCH_EXPORT_PREFIX:-exports/}
      LANGFUSE_S3_BATCH_EXPORT_REGION: ${LANGFUSE_S3_BATCH_EXPORT_REGION:-auto}
      LANGFUSE_S3_BATCH_EXPORT_ENDPOINT: ${LANGFUSE_S3_BATCH_EXPORT_ENDPOINT:-http://minio:9000}
      LANGFUSE_S3_BATCH_EXPORT_EXTERNAL_ENDPOINT: ${LANGFUSE_S3_BATCH_EXPORT_EXTERNAL_ENDPOINT:-http://localhost:9092}
      LANGFUSE_S3_BATCH_EXPORT_ACCESS_KEY_ID: ${LANGFUSE_S3_BATCH_EXPORT_ACCESS_KEY_ID:-minio}
      LANGFUSE_S3_BATCH_EXPORT_SECRET_ACCESS_KEY: ${LANGFUSE_S3_BATCH_EXPORT_SECRET_ACCESS_KEY:-miniosecret} # CHANGEME
      LANGFUSE_S3_BATCH_EXPORT_FORCE_PATH_STYLE: ${LANGFUSE_S3_BATCH_EXPORT_FORCE_PATH_STYLE:-true}
      LANGFUSE_INGESTION_QUEUE_DELAY_MS: ${LANGFUSE_INGESTION_QUEUE_DELAY_MS:-}
      LANGFUSE_INGESTION_CLICKHOUSE_WRITE_INTERVAL_MS: ${LANGFUSE_INGESTION_CLICKHOUSE_WRITE_INTERVAL_MS:-}
      REDIS_HOST: ${REDIS_HOST:-langfuse-redis}
      REDIS_PORT: ${REDIS_PORT:-6379}
      REDIS_AUTH: ${REDIS_AUTH:-myredissecret} # CHANGEME
      REDIS_TLS_ENABLED: ${REDIS_TLS_ENABLED:-false}
      REDIS_TLS_CA: ${REDIS_TLS_CA:-/certs/ca.crt}
      REDIS_TLS_CERT: ${REDIS_TLS_CERT:-/certs/redis.crt}
      REDIS_TLS_KEY: ${REDIS_TLS_KEY:-/certs/redis.key}
      EMAIL_FROM_ADDRESS: ${EMAIL_FROM_ADDRESS:-}
      SMTP_CONNECTION_URL: ${SMTP_CONNECTION_URL:-}
    networks:
      - langfuse-otel-net

  langfuse-web:
    image: docker.io/langfuse/langfuse:3
    restart: always
    depends_on: *langfuse-depends-on
    ports:
      - 3000:3000
    environment:
      <<: *langfuse-worker-env
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET:-mysecret}
      # 初始化 Org / Project
      LANGFUSE_INIT_ORG_ID: ${LANGFUSE_INIT_ORG_ID:-llm-assistance}
      LANGFUSE_INIT_ORG_NAME: ${LANGFUSE_INIT_ORG_NAME:-LLM Assistance Org}
      LANGFUSE_INIT_PROJECT_ID: ${LANGFUSE_INIT_PROJECT_ID:-llm-assistance}
      LANGFUSE_INIT_PROJECT_NAME: ${LANGFUSE_INIT_PROJECT_NAME:-LLM Assistance Project}

      LANGFUSE_INIT_PROJECT_PUBLIC_KEY: ${LANGFUSE__PUBLIC_KEY}
      LANGFUSE_INIT_PROJECT_SECRET_KEY: ${LANGFUSE__SECRET_KEY}

      # 初始化使用者 (選填)
      LANGFUSE_INIT_USER_EMAIL: ${LANGFUSE_INIT_USER_EMAIL:-admin@example.com}
      LANGFUSE_INIT_USER_NAME: ${LANGFUSE_INIT_USER_NAME:-admin}
      LANGFUSE_INIT_USER_PASSWORD: ${LANGFUSE_INIT_USER_PASSWORD:-changeme123}

    networks:
      - langfuse-otel-net
    env_file:
      - .env

  langfuse-clickhouse:
    image: docker.io/clickhouse/clickhouse-server
    restart: always
    # user: "101:101"
    environment:
      CLICKHOUSE_DB: default
      CLICKHOUSE_USER: clickhouse
      CLICKHOUSE_PASSWORD: clickhouse # CHANGEME
    volumes:
      - ./obs_data/langfuse_clickhouse_data:/var/lib/clickhouse
      - ./obs_data/langfuse_clickhouse_logs:/var/log/clickhouse-server
    ports:
      - 127.0.0.1:8123:8123
      - 127.0.0.1:9000:9000
    healthcheck:
      test: wget --no-verbose --tries=1 --spider http://localhost:8123/ping || exit 1
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 1s
    networks:
      - langfuse-otel-net

  langfuse-minio:
    image: docker.io/minio/minio
    restart: always
    entrypoint: sh
    # create the 'langfuse' bucket before starting the service
    command: -c 'mkdir -p /data/langfuse && minio server --address ":9000" --console-address ":9001" /data'
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: miniosecret # CHANGEME
    ports:
      - 9091:9000
      - 127.0.0.1:9092:9001
    volumes:
      - ./obs_data/langfuse_minio_data:/data
    healthcheck:
      test: [ "CMD", "mc", "ready", "local" ]
      interval: 1s
      timeout: 5s
      retries: 5
      start_period: 1s
    networks:
      - langfuse-otel-net

  langfuse-redis:
    image: docker.io/redis:7
    restart: always
    # CHANGEME: row below to secure redis password
    command: >
      --requirepass ${REDIS_AUTH:-myredissecret}
    ports:
      - 127.0.0.1:6380:6379
    healthcheck:
      test: [ "CMD", "redis-cli", "ping" ]
      interval: 3s
      timeout: 10s
      retries: 10
    networks:
      - langfuse-otel-net
  langfuse-postgres:
    image: docker.io/postgres:${POSTGRES_VERSION:-latest}
    restart: always
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres" ]
      interval: 3s
      timeout: 3s
      retries: 10
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres # CHANGEME
      POSTGRES_DB: postgres
    ports:
      - 127.0.0.1:5432:5432
    volumes:
      - ./obs_data/langfuse_postgres_data:/var/lib/postgresql/data
    networks:
      - langfuse-otel-net


```

注意，這樣我就不用再去 langfuse-web `localhost:3000` 取得 key，變成我的key 我自己設定
```
LANGFUSE_INIT_PROJECT_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
LANGFUSE_INIT_PROJECT_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
```

---




### APP
就是先前介紹的 FastAPI
Dockerfile.noteserver 參考補充部分 [Day16 | RAG 的全流程(上)：用 FastAPI 將 RAG 魔法包裝成後端 API](https://ithelp.ithome.com.tw/articles/10383972)

.env
```
LANGFUSE_HOST=http://langfuse-web:3000  # Self-hosted Langfuse URL
# Generate these keys from your self-hosted Langfuse UI at http://localhost:3000
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```


注意 這邊是使用 `LANGFUSE__` 開頭，只要
原廠設定是
```
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_HOST = "https://cloud.langfuse.com" # 🇪🇺 EU region
# LANGFUSE_HOST = "https://us.cloud.langfuse.com" # 🇺🇸 US region
```


```

pip show langfuse
Name: langfuse
Version: 2.60.9
Summary: A client library for accessing langfuse
Home-page:
Author: langfuse
Author-email: developers@langfuse.com
License: MIT
Location: /usr/local/lib/python3.10/site-packages
Requires: anyio, backoff, httpx, idna, packaging, pydantic, requests, wrapt
Required-by:

```




## 實務封裝模式
### 整合外部服務架構
client - factory - tracer

client:`class LangfuseTracer`
 - 跟 Langfuse SDK 直接溝通的低階 API。
- 它就是 Langfuse API 的 wrapper：呼叫 self.client.trace() 建立一個新的 Trace。
- 負責處理 SDK 細節（例如錯誤處理、沒有 client 時 yield None）。

tracer:
`class RAGTracer`
- 封裝成 RAG 業務語意的高階 。
- 這一層是 給 RAG pipeline 用的語意化入口。
- 也就是說，這一層是 高階語意的封裝，讓使用者（或 pipeline）不需要知道底層 Langfuse 細節。

---

### client
```python
class LangfuseTracer:


    def __init__(self, settings: Settings):
        self.settings = settings.langfuse
        self.client: Optional[Langfuse] = None

        if (
            self.settings.enabled
            and self.settings.public_key
            and self.settings.secret_key
        ):
            try:
                self.client = Langfuse(
                    public_key=self.settings.public_key,
                    secret_key=self.settings.secret_key,
                    host=self.settings.host,
                    flush_at=self.settings.flush_at,
                    flush_interval=self.settings.flush_interval,
                    debug=self.settings.debug,
                )
                logger.info(
                    f"Langfuse tracingclient initialized (host: {self.settings.host})"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse: {e}")
                self.client = None
        else:
            logger.info("Langfuse tracing disabled or missing credentials")

    @contextmanager
    def trace_rag_request(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):

        if not self.client:
            yield None
            return

        try:
            # Create a trace using v2 API
            trace = self.client.trace(
                name="rag_request",
                input={"query": query},
                metadata=metadata or {},
                user_id=user_id,
                session_id=session_id,
            )
            yield trace
        except Exception as e:
            logger.error(f"Error creating Langfuse trace: {e}")
            yield None

    def create_span(
        self,
        trace,
        name: str,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):

        if not trace or not self.client:
            return None

        try:
            # Create a span using v2 API
            return self.client.span(
                trace_id=trace.trace_id,
                name=name,
                input=input_data,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(f"Error creating span {name}: {e}")
            return None

    def update_span(
        self,
        span,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: Optional[str] = None,
        status_message: Optional[str] = None,
    ):


        if not span:
            return

        try:
            # For v2 API, we can update spans with end_time and output
            if output is not None:
                # Update the span with output data
                span.update(output=output)
            if metadata:
                span.update(metadata=metadata)
            if level:
                span.update(level=level)
            if status_message:
                span.update(status_message=status_message)
        except Exception as e:
            logger.error(f"Error updating span: {e}")

    def end_span(
        self,
        span,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):


        if not span:
            return

        try:
            # Update with final data if provided
            if output is not None or metadata is not None:
                self.update_span(span, output=output, metadata=metadata)

            # End the span to capture proper timing
            span.end()
        except Exception as e:
            logger.error(f"Error ending span: {e}")

    def flush(self):

        if self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Error flushing Langfuse: {e}")



```
### factory
```python
from functools import lru_cache

from config import get_settings
from services.langfuse.client import LangfuseTracer


@lru_cache(maxsize=1)
def make_langfuse_tracer() -> LangfuseTracer:
    settings = get_settings()
    return LangfuseTracer(settings)

```

- `@lru_cache(maxsize=1)` singleton


### tracer.py

可以自己增加，要trace 甚麼，最基本的 LLM
- request
- build prompt
- generate


```python
from contextlib import contextmanager
from typing import Dict, List

from services.langfuse.client import LangfuseTracer


class RAGTracer:

    def __init__(self, tracer: LangfuseTracer):
        self.tracer = tracer

    @contextmanager
    def trace_request(self, user_id: str, query: str):
        with self.tracer.trace_rag_request(
            query=query,
            user_id=user_id,
            session_id=f"session_{user_id}",
            metadata={"simplified_tracing": True},
        ) as trace:
            try:
                yield trace
            finally:
                if trace:
                    self.tracer.flush()

    @contextmanager
    def trace_embedding(self, trace, query: str):
        span = self.tracer.create_span(
            trace=trace,
            name="query_embedding",
            input_data={"query": query, "query_length": len(query)},
        )
        try:
            yield span
        finally:
            if span:
                self.tracer.update_span(
                    span=span,
                    output={
                        "success": True,
                    },
                )
                span.end()

    def end_embedding(self, span, embedding_vector: list[float]):
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "embedding_length": len(embedding_vector),
                "embedding_vector_preview": embedding_vector[
                    :10
                ],  # 只取前10個元素避免過長
            },
        )
        span.end()

    @contextmanager
    def trace_search(self, trace, query: str, top_k: int, search_mode: str):
        span = self.tracer.create_span(
            trace=trace,
            name="search_retrieval",
            input_data={"query": query, "top_k": top_k, "search_mode": search_mode},
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_search(
        self, span, chunks: List[Dict], arxiv_ids: List[str], total_hits: int
    ):
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "chunks_returned": len(chunks),
                "unique_papers": len(set(arxiv_ids)),
                "total_hits": total_hits,
                "arxiv_ids": list(set(arxiv_ids)),
            },
        )

    @contextmanager
    def trace_rerank(
        self, trace, query: str, vector_weight: float = 0.6, bm25_weight: float = 0.3
    ):
        span = self.tracer.create_span(
            trace=trace,
            name="rerank",
            input_data={
                "query": query,
                "vector_weight": vector_weight,
                "bm25_weight": bm25_weight,
            },
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_rerank(self, span, reranked_chunks: list[dict]):
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "reranked_chunk_count": len(reranked_chunks),
                "top_chunk_ids": [c.get("arxiv_id") for c in reranked_chunks[:10]],
                "top_scores": [c.get("total_score") for c in reranked_chunks[:10]],
            },
        )

    @contextmanager
    def trace_prompt_construction(self, trace, chunks: List[Dict]):
        """Prompt building with timing."""
        span = self.tracer.create_span(
            trace=trace,
            name="prompt_construction",
            input_data={"chunk_count": len(chunks)},
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_prompt(self, span, prompt: str):
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "prompt_length": len(prompt),
                # Don't duplicate the full prompt here since it's in llm_generation input
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            },
        )

    @contextmanager
    def trace_generation(self, trace, model: str, prompt: str):
        span = self.tracer.create_span(
            trace=trace,
            name="llm_generation",
            input_data={"model": model, "prompt_length": len(prompt), "prompt": prompt},
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_generation(self, span, response: str, model: str):
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "response": response,
                "response_length": len(response),
                "model_used": model,
            },
        )

    def end_request(self, trace, response: str, total_duration: float):
        """End main request trace."""
        if not trace:
            return

        try:
            trace.update(
                output={
                    "answer": response,
                    "total_duration_seconds": round(total_duration, 3),
                    "response_length": len(response),
                }
            )
        except Exception:
            pass
```

---


### Code - rag pipeline
```
ask_flow

langfuse_tracer = LangfuseTracer(settings)
rag_tracer = RAGTracer(langfuse_tracer)

with rag_tracer.trace_request(request.user_id, ask_r.query) as trace:
    ├── embedding_span : get_embedding
    ├── search_span : search relevant chunks
    ├── rerank_span : re_rank
    ├── prompt_span: build prompt
    ├── gen_span : generate reponse
rag_tracer.end_request(trace, response.answer, time.time() - start_time)

```
```python

```
1. get_embedding
```python
with rag_tracer.trace_embedding(trace, query=query) as embedding_span:
        query_embedding = get_embedding(query)
    rag_tracer.end_embedding(embedding_span, query_embedding)
```
2. search relevant chunks
```python
with rag_tracer.trace_search(
        trace, query=query, top_k=top_k, search_mode=search_mode
    ) as search_span:
        logger.info(f"Hybrid search enabled: {system_settings.hybrid_search}")
        chunks, sources, msg, arxiv_ids, total_hits = qdrant_client.search(
            query=query,
            query_vector=query_embedding,
            size=top_k * 2,  # retrieve more for reranking
            min_score=0.3,
            hybrid=system_settings.hybrid_search,
            categories=categories,
        )
        rag_tracer.end_search(search_span, chunks, arxiv_ids, total_hits)

```
3. re_ranking
```python
with rag_tracer.trace_rerank(
        trace, query=query, vector_weight=vector_weight, bm25_weight=bm25_weight
    ) as rerank_span:
        reranked = re_ranking(
            chunks,
            query,
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
        )
        rag_tracer.end_rerank(rerank_span, reranked)

```

4. build prompt

```python
    with rag_tracer.trace_prompt_construction(trace, chunks) as prompt_span:
        try:
            prompt_data = ollama_client.prompt_builder.create_structured_prompt(
                query, chunks, system_settings.user_language
            )
            final_prompt = prompt_data["prompt"]
        except Exception:
            final_prompt = ollama_client.prompt_builder.create_rag_prompt(
                query, chunks, system_settings.user_language
            )

        rag_tracer.end_prompt(prompt_span, final_prompt)
```

5. generate reponse

```python
with rag_tracer.trace_generation(trace, model, final_prompt) as gen_span:
        parsed_response, response = await ollama_client.generate_rag_answer(
            query=query,
            chunks=chunks,
            user_language=system_settings.user_language,
            use_structured_output=False,
            temperature=system_settings.temperature,
        )
        rag_tracer.end_generation(gen_span, response, model)
```
