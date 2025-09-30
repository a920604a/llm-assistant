# ============================================================
# 🔧 Makefile - 專案管理工具
# ============================================================
# - 所有服務的生命週期管理 (up, down, restart, logs...)
# - 開發/測試/品管流程一鍵操作
# - Pipeline & Job 執行
#
# 📌 使用方式：
#   make help          # 顯示可用指令
#   make up            # 啟動所有服務
#   make down          # 停止所有服務
# ============================================================


# .env 檔案會自動載入環境變數
ENV_FILE=.env
# 🔍 偵測是否有 GPU (決定 docker-compose 設定檔)
HAS_GPU := $(shell command -v nvidia-smi >/dev/null 2>&1 && echo 1 || echo 0)


# ------------------------------------------------------------
# Compose 定義
# ------------------------------------------------------------
OBS_COMPOSE = docker compose -f docker-compose.obs.yml
STORAGE_COMPOSE = docker compose -f docker-compose.storage.yml
MONITOR_DEV_COMPOSE = docker compose -f docker-compose.monitor.dev.yml
MONITOR_COMPOSE = docker compose -f docker-compose.monitor.yml
DOCKER_FRONTEND_COMPOSE = docker compose -f docker-compose.frontend.yml


# GPU 與非 GPU 的動態 docker-compose
ifeq ($(HAS_GPU),1)
  DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml -f docker-compose.dev.gpu.yml
else
  DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml
endif



# ------------------------------------------------------------
# 共用參數
# ------------------------------------------------------------
PY_DIRS = note apiGateway email arxiv
NETWORKS = monitor-net app-net langfuse-otel-net


# ============================================================
# 📌 基本操作
# ============================================================
.PHONY: test

help: ## 顯示所有可用指令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'


net-create: ## 建立所需的 Docker networks
	@for net in $(NETWORKS); do \
		echo "🔌 檢查/建立 network $$net"; \
		if ! docker network inspect $$net >/dev/null 2>&1; then \
			docker network create $$net --driver bridge; \
			echo "✅ 建立 $$net 完成"; \
		else \
			echo "✅ $$net 已存在"; \
		fi \
	done

up: ## 🚀 啟動所有服務（背景執行）
	$(OBS_COMPOSE) up -d
	$(STORAGE_COMPOSE) up -d
	$(DOCKER_COMPOSE) up -d
# 	$(MONITOR_DEV_COMPOSE) up -d
	sleep 5
	$(MONITOR_COMPOSE) up -d
	$(DOCKER_FRONTEND_COMPOSE) up -d


up-front:
	cd frontend && npm i && npm run dev

down: ## 🛑 停止所有服務
	$(DOCKER_FRONTEND_COMPOSE) down
	$(STORAGE_COMPOSE) down
# 	$(MONITOR_DEV_COMPOSE) down
	$(MONITOR_COMPOSE) down
	$(DOCKER_COMPOSE) down
	$(OBS_COMPOSE) down


restart: down up ## 重啟所有容器


logs: ## 🔍 查看容器日誌（預設 apiGateway）
	$(DOCKER_COMPOSE) logs -f apiGateway


logs-all: ## 查看所有容器日誌
	$(DOCKER_COMPOSE) logs -f



build: ## 重建全部服務
	$(MAKE) net-create
	$(DOCKER_COMPOSE) build
	$(MONITOR_DEV_COMPOSE) build
	$(DOCKER_COMPOSE) exec ollama /bin/bash -c "ollama pull gpt-oss:20b"


shell: ## 進入 apiGateway 容器
	$(DOCKER_COMPOSE) exec apiGateway bash


# ============================================================
# 🧪 測試相關
# ============================================================
test-note: ## 測試 note server (pytest)
	$(DOCKER_COMPOSE) exec noteserver /bin/sh -c "PYTHONPATH=/app pytest tests"

test-apiGateway: ## 測試 apiGateway (pytest)
	$(DOCKER_COMPOSE) exec apiGateway /bin/sh -c "PYTHONPATH=/app pytest tests"

# integration_test:
# 	$(DOCKER_COMPOSE) exec apiGateway /bin/sh -c "PYTHONPATH=/app pytest -v tests/integration"



# ============================================================
# 🧰 Pipeline / Job
# ============================================================
lanhchain: ## 測試 LangChain 客戶端
	$(DOCKER_COMPOSE) exec apiGateway /bin/bash -c "PYTHONPATH=/app python services/langchain_client.py"


ollama-client: ## 測試 Ollama 客戶端
	$(DOCKER_COMPOSE) exec noteserver /bin/bash -c "PYTHONPATH=/app python services/ollama/client.py"

sample_qdrant: ## 測試 Qdrant
	$(DOCKER_COMPOSE) exec noteserver /bin/bash -c "PYTHONPATH=/app python services/qdrant/sample_qdrant.py"

email-trial: ## 測試 Email pipeline
	$(DOCKER_COMPOSE) exec email-flow /bin/bash -c "/opt/conda/envs/prefect/bin/python trial.py"


ingest-arxiv: ## Pipeline - Arxiv 資料匯入
	$(DOCKER_COMPOSE) exec arxiv-flow /bin/bash -c "/opt/conda/envs/prefect/bin/python arxiv_pipeline.py"

email-subscribe: ## Pipeline - Email 訂閱流程
	$(DOCKER_COMPOSE) exec email-flow /bin/bash -c "/opt/conda/envs/prefect/bin/python pipeline.py"

rag: ## Pipeline - RAG (Arxiv)
	$(DOCKER_COMPOSE) exec noteserver /bin/bash -c "PYTHONPATH=/app python arxiv_rag_pipeline.py"




clean: ## 移除所有 volumes (⚠️會清除資料)
	$(MAKE) down
	sudo rm -rf ./data ./obs_data


up-dev:
	$(DOCKER_COMPOSE) up -d note-qdrant noteserver



# ============================================================
# ✅ 品質檢查 (Format + Lint)
# ============================================================
quality_checks: format lint ## 1️⃣ 一鍵執行品質檢查

format: ## 2️⃣ 自動格式化程式碼
	isort $(PY_DIRS)
	black $(PY_DIRS)
	python -m ruff check $(PY_DIRS) --fix



lint: ## 3️⃣ 程式碼靜態檢查
	pylint --rcfile=.pylintrc $(PY_DIRS) || true
	python -m bandit -r $(PY_DIRS) || true


# ============================================================
# 📊 監控服務專用
# ============================================================
down-monitor: ## 停止監控服務
	$(MONITOR_COMPOSE) down

up-monitor: ## 啟動監控服務
	$(MONITOR_COMPOSE) up -d

restart-monitor: ## 重啟監控服務
	$(MONITOR_COMPOSE) down
	$(MONITOR_COMPOSE) up -d
