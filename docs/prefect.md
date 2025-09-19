# Prefect 3.x 在 Docker 環境下的完整部署與自動化 Flow 管理

在現代資料工程中，自動化工作流（Workflow Orchestration）已經成為資料管線建置的核心需求。Prefect 作為一個 Python 原生的工作流編排框架，特別是在 3.x 版本中引入了 Orion API、Deployment、Agent、Work Queue 等新概念，使得 Flow 的排程、監控與分散式執行更加容易。本文將以 **Docker Compose 為基礎環境**，詳細介紹如何在本機建立 Prefect 3.x 流程，自動化 Deployment 以及使用 Agent 執行 Flow。

---

## 1️⃣ Prefect 架構概述

### 1.1 核心組件

Prefect 3.x 的架構可拆解為以下幾個核心組件：

1. **Orion API 與 Web UI**

   * 提供 Flow 的排程、部署、監控介面
   * 提供 REST API，Agent 可透過 API 拿到待執行任務

2. **Deployment**

   * Flow 的可排程實例（相當於 Kubernetes 的 Job 定義）
   * 可綁定排程規則（Cron）、Queue 以及 Flow 參數
   * 透過 CLI 指令 `prefect deployment build` 建立並 apply

3. **Work Queue**

   * 任務隊列，用來分配 Flow 到不同的 Agent
   * Agent 可以監聽一個或多個 Work Queue，根據 queue 名稱拉取任務

4. **Agent**

   * 真正執行 Flow 的執行者（Worker）
   * 會向 Orion API 查詢指定 Queue 的待執行 Deployment
   * 可以運行於不同容器或主機，支援水平擴展

5. **Flow**

   * 使用 Python 製作的工作流
   * 每個 Flow 可包含多個 Task，支持同步/異步、錯誤處理、重試等機制
   * 透過 `@flow` decorator 定義

### 1.2 流程示意

```
[Flow Definition] --> [Deployment] --> [Work Queue] --> [Agent] --> [Flow Execution]
                                       ^
                                       |
                                  [Orion API & UI]
```

---

## 2️⃣ Prefect 版本選擇與相容性

Prefect 2.x 和 3.x 在 API 與 CLI 上差異顯著：

| 版本  | 特點                                                | 適用場景                        |
| --- | ------------------------------------------------- | --------------------------- |
| 2.x | 舊版 CLI，需額外安裝 `prefect-server` 或 Prefect Cloud     | 適合舊專案或 Python 3.7-3.9       |
| 3.x | 新架構，內建 Orion API + UI、Deployment、Agent、Work Queue | 適合 Python 3.10+，支援容器化與自動化部署 |

> ⚠ 如果你的 Python 環境是 3.10，建議使用 **Prefect 3.0.0 \~ 3.4.x**，因為 3.5+ 需要 Python 3.11。

---

## 3️⃣ Docker 環境建置

### 3.1 Dockerfile 範例

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY services/arxivservice/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製 Flow 相關程式碼
COPY ./arxiv /app

# 設定 entrypoint
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
```

### 3.2 requirements.txt

```text
prefect>=3.0.0,<3.5
# 其他依賴，如 aiohttp、pandas、qdrant-client 等
```

> 注意：不要加不存在的 extras，例如 `[client]`，否則會產生 Warning。

---

## 4️⃣ Flow 範例

以抓取 arXiv 論文為例，定義一個簡單 Flow：

```python
# /app/arxiv_pipeline.py
import asyncio
from datetime import datetime, timedelta
from prefect import flow
from tasks.fetch_papers import fetch_papers_task
from tasks.process_pdfs import process_pdfs_task
from tasks.qdrant_index import qdrant_index_task
from tasks.generate_report import generate_report_task

@flow(name="arxiv-pipeline-flow")
def arxiv_pipeline(date_from: str, date_to: str, max_results: int = 10, store_to_db: bool = True):
    papers = asyncio.run(fetch_papers_task(date_from, date_to, max_results))
    if papers:
        pdf_results = asyncio.run(process_pdfs_task(papers, store_to_db=True))
        indexed_count, _ = qdrant_index_task(papers, pdf_results.get("parsed_papers", {}))
    report = generate_report_task({"papers_fetched": len(papers)})
    print(report)


```

---

## 5️⃣ Deployment 與自動化

### 5.1 建立 Deployment

在 Prefect 3.x 中，Deployment 可以透過 CLI 自動建立：
但這邊使用 `entrypoint.sh`
```bash
#!/bin/bash
set -e

# 等待 Orion 啟動
echo "Waiting for Orion API..."
until curl -s http://orion:4200/api/health | grep "true"; do
    echo -n "."
    sleep 2
done
echo "Orion is ready ✅"

# 印 Prefect 版本
prefect version

# 自動建立 Deployment
echo "Creating Deployment..."
prefect deployment build /app/arxiv_pipeline.py:arxiv_pipeline \
  -n "daily_arxiv_pipeline" \
  -q default \
  --cron "*/2 * * * *" \
  --apply \
  --param date_from="20250901" \
  --param date_to="20250918" \
  --param max_results=1

# 啟動 Prefect Agent
echo "Starting Prefect Agent..."
exec prefect agent start -q default

```

* `-n`：Deployment 名稱
* `-q`：指定 Work Queue
* `--cron`：排程設定（測試可用每 2 分鐘，生產可改成每天 9:15）
* `--apply`：自動註冊 Deployment 到 Orion

如果 Flow 有參數，可以在 Deployment 中定義：
```bash
--param date_from=20250901 --param date_to=20250918 --param max_results=5
```

Agent 會拉取 Deployment，帶入這些預設參數執行 Flow。

---

## 6️⃣ Agent 設定與啟動

### 6.1 Docker Compose 範例

```yaml
arxiv-agent:
  build:
    context: .
    dockerfile: ./services/arxivservice/Dockerfile.arxiv
  image: arxiv-agent:latest
  container_name: arxiv-agent
  environment:
    PREFECT_API_URL: http://orion:4200/api
  volumes:
    - ./arxiv:/app
    - ./docker_cache/hf_cache:/root/.cache/huggingface
    - ./data/arxiv_worker:/data
  networks:
    - langfuse-otel-net
```

```yml
```

### 6.2 entrypoint.sh 範例

```bash
#!/bin/bash
echo "Waiting for Orion API..."
until curl -s http://orion:4200/api/health | grep "true"; do
    echo -n "."
    sleep 2
done

echo "Orion is ready ✅"
prefect version
prefect agent start -q default
```

* Agent 啟動後會自動監聽 `default` queue
* Orion API 需先啟動，Agent 才能拉取 Deployment
* `curl` 可檢查 Orion API 健康狀態

---

## 7️⃣ 常見問題

### 7.1 `No such command 'build'`

* 發生原因：Prefect CLI 版本不對
* 解法：確認安裝 Prefect >=3.0.0
* 可透過 `prefect version` 驗證

### 7.2 `/etc/timezone is deprecated`

* Debian/Ubuntu 新版本已不再使用 `/etc/timezone`
* 不影響 Prefect 執行，可以忽略或刪除映射

### 7.3 curl: command not found

* Dockerfile 安裝系統依賴時要加 `curl`

```dockerfile
RUN apt-get update && apt-get install -y curl
```

---

## 8️⃣ 小結

透過 Prefect 3.x + Docker，你可以建立一個完整的自動化資料管線：

1. Flow 定義 Task 並支援異步處理
2. Deployment 將 Flow 封裝成可排程的實例
3. Work Queue 區分不同任務類型
4. Agent 真正負責執行 Flow，可水平擴展
5. Orion 提供 API 與 Web UI 監控，確保任務順利完成

此外，Docker 環境下的自動化腳本可確保：

* 等待 Orion API ready
* 自動建立 Deployment
* 啟動 Agent 並監聽指定 Queue

這樣整個 Prefect 生態就完整運行在容器化環境中，既方便測試也利於生產部署。

---
