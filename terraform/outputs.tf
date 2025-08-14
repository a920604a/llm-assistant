output "postgres_port" {
  value = docker_container.note_db.ports[0].external
}

output "redis_port" {
  value = docker_container.redis.ports[0].external
}

output "minio_console" {
  value = "http://localhost:${docker_container.minio.ports[1].external}"
}

output "minio_api" {
  value = "http://localhost:${docker_container.minio.ports[0].external}"
}

output "open_webui_url" {
  value = "http://localhost:${docker_container.open_webui.ports[0].external}"
}

output "ollama_url" {
  value = "http://localhost:${docker_container.ollama.ports[0].external}"
}
