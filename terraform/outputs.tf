output "minio_console" {
  value = "http://${docker_container.note_storage.name}:9001"
}

output "minio_api" {
  value = "http://${docker_container.note_storage.name}:9000"
}

output "postgres_url" {
  value = "postgresql://${var.db_user}:${var.db_password}@${docker_container.note_db.name}:5432/${var.db_name}"
}

output "qdrant_url" {
  value = "http://${docker_container.note_qdrant.name}:6333"
}

output "ollama_url" {
  value = "http://${docker_container.ollama.name}:11434"
}

output "open_webui_url" {
  value = "http://${docker_container.open_webui.name}:8080"
}

output "redis_url" {
  value = "redis://${docker_container.redis.name}:6379"
}

output "worker_flower_url" {
  value = "http://${docker_container.flower.name}:5555"
}
