# Observability & Monitoring：以 arXiv 驅動的個人化 RAG 平台為例

> 作者：小安｜日期：2025-09-05
> 針對後端、MLOps、DevOps 的 Observability 實務分享

---

## 1. 前言：為什麼 Observability / Monitoring 很重要

在現代複雜系統中，僅靠日誌或單一指標很難掌握系統健康狀態。對於我們的專案——一個結合 **arXiv Ingestion Pipeline、RAG Chat Engine、Email 訂閱服務** 的個人化資訊平台，系統包含多個微服務、共享資料庫、向量資料庫以及背景任務。

面對這樣的架構，我們需要：

| 特性     | Monitoring（監控）    | Observability（可觀測性） |
| ------ | ----------------- | ------------------- |
| **目標** | 確保服務運行健康          | 理解系統內部運作，定位問題根源     |
| **焦點** | 表面指標、已知異常         | 流程行為、未知問題           |
| **功能** | 追蹤已知指標、設告警門檻、發出警報 | 分析未知異常、性能優化、故障調查    |
| **結果** | 只能提示「發生了什麼」       | 能分析「為什麼發生」          |


換句話說，我們要：

* 確保 **服務可用性**（API、Notes Service、背景任務）
* 監控 **性能瓶頸**（（Prefect Flow / Task 延遲、LLM 調用延遲）
* 快速 **定位異常**（API 過頻、Redis/DB 錯誤、資源耗盡）


---

## 2. Observability 核心概念

我們將觀測重點分為三大類：Metrics、Tracing、Alert / Logging。

| 類別              | Monitoring（監控）                                   | Observability（可觀測性）                            |
| --------------- | ------------------------------------------------ | ---------------------------------------------- |
| **Metrics**     | CPU/Memory/Disk、API 請求數、Redis/DB 操作次數 | LLM 延遲、Redis/DB latency、API 路由細節 |
| **Tracing**     |                      -                  | RAG 問答流程全程追蹤、Prefect Flow / Task 流程分析             |
| **Alert / Log** | 服務不可用、API 過頻、資源異常告警                              | 日誌與異常追蹤、定位未知問題                                 |

> 簡單來說，Metrics 量化、Tracing 跟蹤流程、Alert / Log 告訴你系統哪裡出問題。

---

## 3. 專案實作經驗

### 3.1 工具選型

* **Prometheus**：收集系統與應用 Metrics
* **Grafana**：可視化 Metrics 與 Tracing 結果
* **AlertManager**：設定告警規則，發送通知（Slack / PagerDuty / Email）
* **Langfuse（選配）**：LLM 調用觀測

### 3.2 Metrics 收集策略

* **API 路由**：請求次數（Counter）、延遲時間（Histogram）
* **Redis / DB**：GET/SET 次數、查詢延遲、錯誤率
* **LLM 調用**：延遲、成功率、異常次數（可用 Langfuse 擴充細節觀測）

### 3.3 Tracing 策略

* RAG 問答流程全程追蹤，從 Query Rewrite → Hybrid Search → Rerank → Prompt 組裝 → LLM 回覆
* Background Tasks（Ingest / Email / Notes Service）流程追蹤，方便分析瓶頸


### 3.4 Alert / Log 設計

* **服務可用性**：Instance down、Network unreachable
* **資源異常**：CPU、Memory、Disk 空間使用率
* **API 過頻 / 異常行為**：單個 endpoint 請求速率過高、返回錯誤率過高
* 所有告警透過 **AlertManager** 發送通知

---

## 4. Observability 架構圖示意

```mermaid
flowchart LR
    subgraph App[arXiv RAG Platform]
        FE[Web Frontend]
        API[API Gateway]
        NS[Notes Service RAG ]
        BG[Background Tasks: Ingest / Email]
        DB[PostgreSQL / MinIO / Qdrant / Redis]
        LLM[LLM Service]
    end

    subgraph Observability
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[AlertManager]
        LF[Langfuse /Web]
    end

    FE --> API --> NS
    NS --> DB
    BG --> DB
    NS --> LLM

    DB --> PROM
    NS --> PROM
    BG --> PROM
    API --> PROM
    LLM --> PROM

    LLM --> LF

    PROM --> GRAF
    PROM --> ALERT
```

> 上圖示意整個平台與 Observability 架構關係，Metrics / Tracing 由 Prometheus 收集，Grafana 可視化，AlertManager 負責告警。

---

## 5. 實務心得

1. **程式內 Metrics 裝飾器很重要**：decorator 可捕捉每個 FastAPI 路由、Redis、DB 調用。
2. **Tracing 幫助定位瓶頸**：RAG 問答流程複雜，多個步驟，Tracing 能精確指出延遲來源（如 reranker 或 LLM 調用）。
3. **Alert 規則需合理**：過於敏感會造成告警疲勞，過於寬鬆又可能延誤問題。設定 threshold 要結合實際系統負載。

---

## 6. 小結

在複雜的個人化 RAG 平台中，Observability / Monitoring 不僅是運維工具，更是**開發與性能優化的重要依據**。
透過 **Metrics、Tracing、Alert/Logging** 組合，以及 **程式內自動收集與 Prometheus / Grafana / AlertManager** 的整合，我們可以：

* 快速掌握系統健康狀態
* 精準定位性能瓶頸與錯誤
* 提升服務穩定性與用戶體驗
> Langfuse 提供 LLM 層的可選觀測，方便 RAG 調優與細節追蹤。

---

✅ **重點提醒**：

* Metrics：量化指標、成功率與延遲
* Tracing：流程追蹤、瓶頸定位
* Alert / Log：即時告警、異常通知

---


## 架構
| 組件                                                            | 功能                                            | 類型         |
| ------------------------------------------------------------- | --------------------------------------------- | ---------- |
| Prometheus                                                    | 收集各種 Metrics（CPU、Memory、API 請求數、Redis/DB 指標等） | Monitoring |
| Grafana                                                       | 將收集到的 Metrics 可視化、建立 Dashboard                | Monitoring |
| AlertManager                                                  | 根據規則、發送通知                                   | Monitoring |
| Node Exporter / cAdvisor / Redis Exporter / Blackbox Exporter | 系統資源 / Docker / Redis / 外部端點狀態監控              | Monitoring |
| Prefect Exporter                      | 追蹤 Prefect Flow / Task 運行狀態、延遲、異常  | Observability |
| Langfuse              | 追蹤 LLM 調用、RAG 流程、可存儲與查詢 trace / event / log，支持跨服務追蹤              | Observability |



##　附錄
```yml
networks:
  monitor-net:
    external: true
  langfuse-otel-net:
    external: true
  app-net:
    external: true

services:
  prometheus:
    image: prom/prometheus
    user: "1001"
    volumes:
      - ./monitor/prometheus:/etc/config
      - ./monitor_data/prometheus_data:/prometheus
      - ./monitor/rules:/etc/prometheus/rules
    ports:
      - "127.0.0.1:9090:9090"
    command:
      - "--config.file=/etc/config/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.console.libraries=/usr/share/prometheus/console_libraries"
      - "--web.console.templates=/usr/share/prometheus/consoles"
    networks:
      - monitor-net
      - langfuse-otel-net
      - app-net

  alertmanager:
    build:
      context: .
      dockerfile: ./services/alertmanager/Dockerfile.alertmanager
    image: alertmanager:latest
    container_name: alertmanager
    restart: always
    networks:
      - monitor-net
    ports:
      - 127.0.0.1:9093:9093
    env_file:
      - .env

  grafana:
    image: grafana/grafana-enterprise
    user: "472"
    ports:
      - "0.0.0.0:3002:3000"
    volumes:
      - ./monitor/dashboards:/var/lib/grafana/dashboards # dashboard JSON, Node Exporter Full: 1860 , cAdvisor Exporter: 14282 , Prometheus Blackbox Exporter: 7587
      - ./monitor/provisioning:/etc/grafana/provisioning # provisioning 設定
    environment:
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
      - GF_SECURITY_ADMIN_USER=${GF_SECURITY_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GF_SECURITY_ADMIN_PASSWORD} # 可設定 Grafana admin 密碼
      - GF_INSTALL_PLUGINS=vertamedia-clickhouse-datasource
    restart: always
    networks:
      - monitor-net

  node-exporter:
    image: prom/node-exporter:v1.8.2
    ports:
      - "127.0.0.1:9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitor-net

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.1
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - monitor-net

  blackbox-exporter:
    image: prom/blackbox-exporter
    container_name: blackbox-exporter
    ports:
      - "9115:9115"
    volumes:
      - ./monitor/blackbox:/config
    command:
      - "--config.file=/config/blackbox.yml"
    networks:
      - monitor-net
      - langfuse-otel-net

  redis-exporter:
    image: oliver006/redis_exporter:v1.41.0
    container_name: redis_exporter
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis:6379
    networks:
      - langfuse-otel-net

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
