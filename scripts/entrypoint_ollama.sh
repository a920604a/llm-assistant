#!/bin/bash
set -e

# 函式：檢查模型是否存在，若不存在才 pull
pull_model_if_needed() {
    local model=$1
    if ! ollama list | grep -q "$model"; then
        echo "🔴 Pulling Ollama $model model..."
        ollama pull "$model"
        echo "🟢 $model ready!"
    else
        echo "🟢 $model already exists!"
    fi
}

# Start Ollama in the background
/bin/ollama serve &
pid=$!

# Wait until Ollama API is available
sleep 2


# 模型列表
models=("gpt-oss:20b" "llama3.2:1b" "llama3.2:3b")

# 迭代拉模型
for model in "${models[@]}"; do
    pull_model_if_needed "$model"
done

# 等待 Ollama process 結束
wait $pid
