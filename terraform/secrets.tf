# Local secret file (可改為雲端 Secret Manager)
resource "local_file" "env_file" {
  filename = "${path.module}/.env"
  content  = <<EOF
DATABASE_URL=postgresql://${var.db_user}:${var.db_password}@${docker_container.note_db.name}:5432/${var.db_name}

MINIO_ENDPOINT=http://${docker_container.note_storage.name}:9000
MINIO_ACCESS_KEY=${var.minio_user}
MINIO_SECRET_KEY=${var.minio_password}
MINIO_BUCKET=note-md

QDRANT_URL=http://${docker_container.note_qdrant.name}:6333

OLLAMA_API_URL=http://${docker_container.ollama.name}:11434
EOF
}
