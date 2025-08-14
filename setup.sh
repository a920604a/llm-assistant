# 1️⃣ build 自訂 Docker image
docker build -t mcpclient:latest ./ -f ./services/mcpclient/Dockerfile.mcpclient && \
docker build -t noteserver:latest ./ -f ./services/noteservice/Dockerfile.noteserver && \
docker build -t worker:latest ./ -f ./services/celeryworker/Dockerfile.worker && \


# 2️⃣ 進入 terraform 專案目錄
cd ~/Desktop/llm-assistant/terraform && \

# 3️⃣ 初始化 Terraform
terraform init && \


# 4️⃣ 檢查 image 是否成功
docker images | grep -E "mcpclient|noteserver|worker" && \

# 5️⃣ Terraform 預覽
terraform plan && \

# 6️⃣ Terraform 套用
terraform apply
