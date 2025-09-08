#!/bin/sh
set -e

# 等待 MinIO server 啟動
echo "Waiting for MinIO..."

python -m storage.wait_minio

# 初始化 Firebase
python -c "from firebase_admin import credentials, initialize_app; import os; from config import FIREBASE_KEY_PATH; cred = credentials.Certificate(f'{FIREBASE_KEY_PATH}/serviceAccountKey.json'); initialize_app(cred)"

# 建立 bucket
python -m storage.minio

echo "done for create bucket on MinIO..."


# --- 判斷要啟動 worker 還是 beat ---
if [ "$1" = "worker" ]; then
    exec celery -A celery_app.celery_app worker --concurrency=4 --queues email -n worker.email_alarm@%h --loglevel=info
elif [ "$1" = "beat" ]; then
    exec celery -A celery_app.celery_app beat --loglevel=info
else
    exec "$@"
fi
