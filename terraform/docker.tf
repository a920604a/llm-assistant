# PostgreSQL
resource "docker_container" "note_db" {
  image = "postgres:15"
  name  = "note-db"
  env = [
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
    "POSTGRES_DB=${var.db_name}"
  ]
  ports {
    internal = 5432
    external = 5411
  }
  volumes {
    host_path      = "${path.module}/data/note_db"
    container_path = "/var/lib/postgresql/data"
  }
}

# Redis
resource "docker_container" "redis" {
  image = "redis:7"
  name  = "note-worker-redis"
  ports {
    internal = 6379
    external = 6379
  }
}

# MinIO
resource "docker_container" "minio" {
  image = "minio/minio"
  name  = "note-minio"
  command = "server /data --console-address ':9001'"
  env = [
    "MINIO_ROOT_USER=${var.minio_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_password}"
  ]
  ports {
    internal = 9000
    external = 9111
  }
  ports {
    internal = 9001
    external = 9001
  }
  volumes {
    host_path      = "${path.module}/data/note-storage"
    container_path = "/data"
  }
}

# Ollama
resource "docker_container" "ollama" {
  image = "ollama/ollama"
  name  = "mcphost-ollama"
  ports {
    internal = 11434
    external = 11434
  }
  # GPU driver 需 host 配置好 nvidia runtime
}

# Open-WebUI
resource "docker_container" "open_webui" {
  image = "ghcr.io/open-webui/open-webui:cuda"
  name  = "open-webui"
  env = [
    "WEBUI_USERNAME=${var.webui_user}",
    "WEBUI_PASSWORD=${var.webui_password}",
    "OLLAMA_BASE_URL=http://ollama:11434"
  ]
  ports {
    internal = 8080
    external = 3011
  }
  depends_on = [docker_container.ollama]
}
