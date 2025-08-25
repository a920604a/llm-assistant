# .env 檔案會自動載入環境變數
ENV_FILE=.env
HAS_GPU := $(shell command -v nvidia-smi >/dev/null 2>&1 && echo 1 || echo 0)

# 動態決定 docker compose 指令
ifeq ($(HAS_GPU),1)
  DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml -f docker-compose.dev.gpu.yml
else
  DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml
endif

MONITOR_DEV_COMPOSE = docker compose -f docker-compose.monitor.dev.yml
MONITOR_COMPOSE = docker compose -f docker-compose.monitor.yml
PY_DIRS = note mcpclient

NETWORK_NAME = monitor-net app-net

.PHONY: test


net-create: ## 建立共用 Docker network（若不存在）
	@echo "🔌 檢查/建立 network $(NETWORK_NAME)"
	@if ! docker network inspect $(NETWORK_NAME) >/dev/null 2>&1; then \
		docker network create $(NETWORK_NAME) --driver bridge; \
		echo "✅ 建立 $(NETWORK_NAME) 完成"; \
	else \
		echo "✅ $(NETWORK_NAME) 已存在"; \
	fi
# 啟動所有容器（背景執行）
up:
	$(MAKE) net-create
	$(DOCKER_COMPOSE) up -d
	$(MONITOR_DEV_COMPOSE) up -d
# 	$(MONITOR_COMPOSE) up -d


up-front:
	cd frontend && npm i && npm run dev

# 停止所有容器
down:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) down
	$(MONITOR_DEV_COMPOSE) down
# 	$(MONITOR_COMPOSE) down

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
