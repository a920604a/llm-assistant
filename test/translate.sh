#!/bin/bash

TEXT="$1"
PROMPT="Please translate the following English sentence into Traditional Chinese:\n\n$TEXT"

curl http://localhost:11434/api/generate \
  -s \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"llama2:7b\",
    \"prompt\": \"$PROMPT\",
    \"stream\": false,
    \"temperature\": 0.3
  }" | jq -r '.response'
