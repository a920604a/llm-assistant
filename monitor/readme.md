| 元件                        | 功能                | 監控範圍 / 指標                                          |
| ------------------------- | ----------------- | -------------------------------------------------- |
| **Prometheus**            | 核心監控與 metrics 聚合  | 負責從各種 Exporter 抓取指標、存儲時序資料、提供 API 給 Grafana 查詢與警報。 |
| **Node Exporter**         | 主機系統資源監控          | CPU 使用率、Memory 使用量、磁碟 I/O、網路流量等。                   |
| **cAdvisor**              | Docker 容器層級監控     | 容器 CPU、Memory、磁碟與網路使用量、容器數量、啟動時間等。                 |
| **Blackbox Exporter**     | 外部服務可用性監控         | HTTP/HTTPS/TCP/ICMP 健康檢查，回應狀態、延遲、可用性。              |
| **Celery Exporter**       | Celery 任務隊列監控     | Worker 狀態、任務數量、任務完成/失敗率、事件監聽。                      |
| **Redis Exporter**        | Redis 指標監控        | Memory 使用、連線數、key 數量、命中率、持久化狀態等。                   |
| **FastAPI 應用自定義 metrics** | App 層監控           | 透過 `/metrics` endpoint 提供自定義指標，例如請求數量、延遲、錯誤率。      |
| **Grafana**               | Dashboard 與 Alert | 對 Prometheus 指標可視化、建立告警、生成統計圖表與儀表板。                |



```mermiad
flowchart TB
  %% ======================
  %% Exporters & App Metrics
  %% ======================
  subgraph EXPORTERS
    NodeExporter[node-exporter<br/>主機系統資源]
    cAdvisor[cAdvisor<br/>Docker 容器資源]
    CeleryExporter[celery_exporter<br/>Celery queue/worker metrics]
    RedisExporter[redis_exporter<br/>Redis 指標]
    BlackboxExporter[blackbox-exporter<br/>HTTP/TCP/ICMP 健康檢查]
    FastAPIApp[Noteserver / MCPClient<br/>自訂 application metrics]
    MinIO[MinIO / S3-compatible<br/>storage metrics]
    GrafanaWeb[Grafana HTTP probe]
    Portainer[Portainer HTTP probe]
    LangfuseWeb[Langfuse Web UI probe]
  end

  %% ======================
  %% Prometheus
  %% ======================
  subgraph PROMETHEUS[Prometheus<br/>Metrics 聚合 & Scrape]
    direction TB
  end

  %% ======================
  %% Grafana Dashboard
  %% ======================
  subgraph GRAFANA[Grafana<br/>Dashboard & Alert]
    direction TB
  end

  %% ======================
  %% 連線關係
  %% ======================
  NodeExporter -->|metrics scrape| PROMETHEUS
  cAdvisor -->|metrics scrape| PROMETHEUS
  CeleryExporter -->|metrics scrape| PROMETHEUS
  RedisExporter -->|metrics scrape| PROMETHEUS
  FastAPIApp -->|metrics scrape| PROMETHEUS
  MinIO -->|metrics scrape| PROMETHEUS
  BlackboxExporter -->|probe metrics| PROMETHEUS
  GrafanaWeb -->|probe metrics| BlackboxExporter
  Portainer -->|probe metrics| BlackboxExporter
  LangfuseWeb -->|probe metrics| BlackboxExporter

  PROMETHEUS -->|提供 metrics API| GRAFANA

```
