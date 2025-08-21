# .env 檔案會自動載入環境變數
ENV_FILE=.env
HAS_GPU := $(shell command -v nvidia-smi >/dev/null 2>&1 && echo 1 || echo 0)

# 動態決定 docker compose 指令
ifeq ($(HAS_GPU),1)
  DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml -f docker-compose.dev.gpu.yml
else
  DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml
endif

MONITOR_COMPOSE = docker compose -f docker-compose.monitor.dev.yml
PY_DIRS = note mcpclient


.PHONY: test

# 啟動所有容器（背景執行）
up:
	$(DOCKER_COMPOSE) up -d
	$(MONITOR_COMPOSE) up -d


up-front:
	cd frontend && npm i && npm run dev

# 停止所有容器
down:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) down
	$(MONITOR_COMPOSE) down

# 重啟所有容器
restart:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) up -d

# 查看容器日誌（預設看 mcpclient）
logs:
	$(DOCKER_COMPOSE) logs -f mcpclient

# 查看所有容器日誌
logs-all:
	$(DOCKER_COMPOSE) logs -f

# 重建 mcpclient 服務
build-mcpclient:
	$(DOCKER_COMPOSE) build mcpclient

# 重建全部服務
build:
	$(DOCKER_COMPOSE) build

# 進入 mcpclient 容器
shell:
	$(DOCKER_COMPOSE) exec mcpclient bash

# 測試 (需先裝 pytest)
test:
# 	$(DOCKER_COMPOSE) exec mcpclient /bin/sh -c "PYTHONPATH=/app pytest -v tests/"
	$(DOCKER_COMPOSE) exec mcpclient /bin/sh -c "PYTHONPATH=/app python services/langchain_client.py"

# test:
# 	$(DOCKER_COMPOSE) exec mcpclient /bin/sh -c "PYTHONPATH=/app pytest -v tests"

# integration_test:
# 	$(DOCKER_COMPOSE) exec mcpclient /bin/sh -c "PYTHONPATH=/app pytest -v tests/integration"

# 移除所有 volumes (⚠️會清除資料)
clean:
	$(MAKE) down
	sudo rm -rf ./data


up-dev:
	$(DOCKER_COMPOSE) up -d note-qdrant noteserver




ingest-arxiv:
	$(DOCKER_COMPOSE) exec noteserver /bin/sh -c "PYTHONPATH=/app python /app/arxiv_ingestion/flows/arxiv_pipeline.py"

search-arxiv:
	$(DOCKER_COMPOSE) exec noteserver /bin/sh -c "PYTHONPATH=/app python /app/arxiv_ingestion/flows/arxiv_rag_pipeline.py"




# 1️⃣ 一鍵檢查品質
quality_checks: format lint

# 2️⃣ 格式化程式碼
format:
	isort $(PY_DIRS)
	black $(PY_DIRS)
	python -m ruff check $(PY_DIRS) --fix


# 3️⃣ 代碼檢查
lint:
	pylint $(PY_DIRS) || true
	python -m bandit -r $(PY_DIRS) || true
