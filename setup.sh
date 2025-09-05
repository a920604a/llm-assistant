#! /bin/bash


# 1️⃣ build 自訂 Docker image
docker build -t apiGateway:latest ./ -f ./services/apiGateway/Dockerfile.apiGateway && \
docker build -t noteserver:latest ./ -f ./services/noteservice/Dockerfile.noteserver && \
docker build -t arxiv-worker:latest ./ -f ./services/arxivservice/Dockerfile.arxiv && \
docker build -t arxiv-beat:latest ./ -f ./services/arxivservice/Dockerfile.arxiv && \
docker build -t email-worker:latest ./ -f ./services/emailservice/Dockerfile.email && \
docker build -t email-beat:latest ./ -f ./services/emailservice/Dockerfile.email && \
docker build -t nginx:latest ./ -f ./services/frontend/Dockerfile.nginx && \



# 2️⃣ 進入 terraform 專案目錄
cd ~/Desktop/llm-assistant/terraform && \

# 3️⃣ 初始化 Terraform
terraform init && \


# 4️⃣ 檢查 image 是否成功
docker images | grep -E "apiGateway|noteserver|arxiv-worker|email-worker|arxiv-beat|email-beat" && \

# 5️⃣ Terraform 預覽
terraform plan && \

# 6️⃣ Terraform 套用
terraform apply


# 檢查 Docker container 狀態
echo "🔍 檢查 container 狀態..."

# 要檢查的 container 名稱
containers=("apiGateway" "noteserver" "arxiv-worker" "email-worker" "arxiv-beat" "email-beat" "open-webui" "note-db" "note-qdrant" "redis" "flower")

for name in "${containers[@]}"; do
    status=$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null || echo "not found")
    if [ "$status" = "running" ]; then
        echo "✅ $name is running"
    else
        echo "❌ $name is NOT running (status: $status)"
    fi
done
