resource "docker_network" "llm_network" {
  name = "llm-network"
}
resource "docker_container" "nginx" {
  name  = "nginx"
  image = "nginx:latest"

  networks_advanced {
    name = docker_network.llm_network.name
  }
  ports {
    internal = 80
    external = 80
  }
  depends_on = [
    docker_container.mcpclient
  ]
  volumes {
    host_path      = abspath("${path.module}/../services/frontend/nginx.conf") # 修正路徑
    container_path = "/etc/nginx/nginx.conf"
  }

}


resource "docker_container" "ollama" {
  name  = "mcphost-ollama"
  image = "ollama/ollama:latest"

  networks_advanced {
    name = docker_network.llm_network.name
  }
  ports {
    internal = 11434
    external = 11434
  }

  volumes {
    host_path      = abspath("${path.module}/../ollama_models")
    container_path = "/root/.ollama"
  }

  runtime = "nvidia"
  env = [
    "NVIDIA_VISIBLE_DEVICES=all"
  ]
}

resource "docker_container" "open_webui" {
  name  = "open-webui"
  image = "ghcr.io/open-webui/open-webui:cuda"
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 8080
    external = 3011
  }

  volumes {
    host_path      = abspath("${path.module}/../data/open-webui")
    container_path = "/app/backend/data"
  }

  runtime = "nvidia"

  env = [
    "WEBUI_USERNAME=${var.webui_user}",
    "WEBUI_PASSWORD=${var.webui_password}",
    "OLLAMA_BASE_URL=http://${docker_container.ollama.name}:11434"
  ]

  depends_on = [
    docker_container.ollama
  ]
}

resource "docker_container" "mcpclient" {
  name  = "mcpclient"
  image = "mcpclient:latest" # TODO , because custom docker image
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 8000
    external = 8011
  }

  volumes {
    host_path      = abspath("${path.module}/../mcpclient")
    container_path = "/app"
  }

  env = [
    "OLLAMA_API_URL=http://${docker_container.ollama.name}:11434",
  ]

  depends_on = [
    docker_container.ollama
  ]
}

resource "docker_container" "noteserver" {
  name  = "noteserver"
  image = "noteserver:latest" # TODO , because custom docker image
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 8000
    external = 8022
  }

  volumes {
    host_path      = abspath("${path.module}/../note")
    container_path = "/app"
  }

  env = [
    for line in split("\n", file("${path.module}/../.env")) : line if length(trimspace(line)) > 0
  ]

  depends_on = [
    docker_container.note_db,
    docker_container.redis,
    docker_container.note_qdrant
  ]
}

resource "docker_container" "note_qdrant" {
  name  = "note-qdrant"
  image = "qdrant/qdrant"
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 6333
    external = 6333
  }

  volumes {
    host_path      = abspath("${path.module}/../data/qdrant_data")
    container_path = "/qdrant/storage"
  }
}

resource "docker_container" "note_db" {
  name  = "note-db"
  image = "postgres:15"
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 5432
    external = 5411
  }

  volumes {
    host_path      = abspath("${path.module}/../data/note_db")
    container_path = "/var/lib/postgresql/data"
  }

  volumes {
    host_path      = abspath("${path.module}/../db/init-scripts")
    container_path = "/docker-entrypoint-initdb.d"
    read_only      = true
  }

  env = [
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
    "POSTGRES_DB=${var.db_name}"
  ]
}

resource "docker_container" "note_storage" {
  name  = "note-sotorage"
  image = "minio/minio:latest"
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 9000
    external = 9111
  }
  ports {
    internal = 9001
    external = 9001
  }

  volumes {
    host_path      = abspath("${path.module}/../data/note-storage")
    container_path = "/data"
  }

  env = [
    "MINIO_ROOT_USER=${var.minio_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_password}"
  ]

  command = ["server", "/data", "--console-address", ":9001"]
}

resource "docker_container" "redis" {
  name  = "redis"
  image = "redis:7"
  networks_advanced {
    name = docker_network.llm_network.name
  }

  ports {
    internal = 6379
    external = 6379
  }
}

resource "docker_container" "arxiv-worker" {
  name  = "arxiv-worker"
  image = "arxiv-worker:latest" # TODO , because custom docker image
  networks_advanced {
    name = docker_network.llm_network.name
  }

  command = ["celery", "-A", "celery_app.celery_app", "worker", "--concurrency=4", "-Q", "notes", "-n", "worker.import_md@%h", "--loglevel=info"]

  volumes {
    host_path      = abspath("${path.module}/../arxiv")
    container_path = "/app"
  }

  volumes {
    host_path      = abspath("${path.module}/../docker_cache/hf_cache")
    container_path = "/root/.cache/huggingface"
  }

  # 只有 arxiv-worker 有
  volumes {
    host_path      = abspath("${path.module}/../data/arxiv_worker")
    container_path = "/data"
  }


  env = [
    for line in split("\n", file("${path.module}/../.env")) : line if length(trimspace(line)) > 0
  ]

  depends_on = [
    docker_container.redis,
    docker_container.note_db,
    docker_container.note_qdrant,
    docker_container.note_storage
  ]
}

resource "docker_container" "arxiv-beat" {
  name  = "arxiv-beat"
  image = "arxiv-beat:latest" # TODO , because custom docker image
  networks_advanced {
    name = docker_network.llm_network.name
  }

  command = ["celery", "-A", "celery_app.celery_app", "beat", "--loglevel=info"]

  volumes {
    host_path      = abspath("${path.module}/../arxiv")
    container_path = "/app"
  }
  volumes {
    host_path      = abspath("${path.module}/../docker_cache/hf_cache")
    container_path = "/root/.cache/huggingface"
  }

  env = [
    for line in split("\n", file("${path.module}/../.env")) : line if length(trimspace(line)) > 0
  ]

  depends_on = [
    docker_container.redis,
    docker_container.note_db
  ]
}


resource "docker_container" "flower" {
  name  = "flower"
  image = "mher/flower:0.9.7"

  networks_advanced {
    name = docker_network.llm_network.name
  }
  ports {
    internal = 5555
    external = 5555
  }

  command = ["flower", "--broker=redis://redis:6379/0", "--port=5555"]

  depends_on = [
    docker_container.redis
  ]
}



resource "docker_container" "email-worker" {
  name  = "email-worker"
  image = "email-worker:latest" # TODO , because custom docker image
  networks_advanced {
    name = docker_network.llm_network.name
  }

  command = ["celery", "-A", "celery_app.celery_app", "worker", "--concurrency=4", "-Q", "email", "-n", "worker.email_alarm@%h", "--loglevel=info"]

  volumes {
    host_path      = abspath("${path.module}/../email")
    container_path = "/app"
  }
  volumes {
    host_path      = abspath("${path.module}/../docker_cache/hf_cache")
    container_path = "/root/.cache/huggingface"
  }

  env = [
    for line in split("\n", file("${path.module}/../.env")) : line if length(trimspace(line)) > 0
  ]

  depends_on = [
    docker_container.redis,
    docker_container.note_db,
    docker_container.note_storage
  ]

}

resource "docker_container" "email-beat" {
  name  = "email-beat"
  image = "email-beat:latest" # TODO , because custom docker image
  networks_advanced {
    name = docker_network.llm_network.name
  }

  command = ["celery", "-A", "celery_app.celery_app", "beat", "--loglevel=info"]

  volumes {
    host_path      = abspath("${path.module}/../email")
    container_path = "/app"
  }
  volumes {
    host_path      = abspath("${path.module}/../docker_cache/hf_cache")
    container_path = "/root/.cache/huggingface"
  }

  env = [
    for line in split("\n", file("${path.module}/../.env")) : line if length(trimspace(line)) > 0
  ]

  depends_on = [
    docker_container.redis,
    docker_container.email-worker,
  ]
}
