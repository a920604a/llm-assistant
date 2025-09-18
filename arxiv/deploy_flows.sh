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

# 建立 Work Pool / Queue（容錯）
prefect work-pool create default --type process || true
prefect work-queue create ingest-queue --pool default || true

# 部署 flow
echo "Deploying flows..."
python /app/prefect_entrypoint.py
