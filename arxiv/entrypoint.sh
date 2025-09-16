#!/bin/sh
set -e
# --- 判斷要啟動 worker 還是 beat ---
if [ "$1" = "worker" ]; then
    exec celery -A celery_app.celery_app worker --concurrency=4 --queues notes -n worker.ingest_arxiv@%h --loglevel=info
elif [ "$1" = "beat" ]; then
    exec celery -A celery_app.celery_app beat --loglevel=info
else
    exec "$@"
fi
