# .env 檔案會自動載入環境變數
ENV_FILE=.env
DOCKER_COMPOSE=docker-compose -f docker-compose.dev.yml
DEV_COMPOSE=docker-compose -f docker-compose.monitor.dev.yml


# 啟動所有容器（背景執行）
up:
	$(DOCKER_COMPOSE) up -d
	$(DEV_COMPOSE) up -d


up-front:
	cd frontend && npm i && npm run dev

# 停止所有容器
down:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) down
	$(DEV_COMPOSE)  down

# 重啟所有容器
restart:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) up -d

# 查看容器日誌（預設看 api）
logs:
	$(DOCKER_COMPOSE) logs -f api

# 查看所有容器日誌
logs-all:
	$(DOCKER_COMPOSE) logs -f

# 重建 API 服務
build-api:
	$(DOCKER_COMPOSE) build api

# 重建全部服務
build:
	$(DOCKER_COMPOSE) build

# 進入 API 容器
shell:
	$(DOCKER_COMPOSE) exec api bash

# 測試 (需先裝 pytest)
test:
	$(DOCKER_COMPOSE) exec api pytest /test

# 移除所有 volumes (⚠️會清除資料)
clean:
	sudo rm -rf ./data
	$(DOCKER_COMPOSE) down -v
