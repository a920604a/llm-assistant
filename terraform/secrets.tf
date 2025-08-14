# Local secret file (可改為雲端 Secret Manager)
resource "local_file" "env_file" {
  filename = "${path.module}/.env"
  content  = <<EOF
POSTGRES_USER=${var.db_user}
POSTGRES_PASSWORD=${var.db_password}
POSTGRES_DB=${var.db_name}
MINIO_ROOT_USER=${var.minio_user}
MINIO_ROOT_PASSWORD=${var.minio_password}
WEBUI_USERNAME=${var.webui_user}
WEBUI_PASSWORD=${var.webui_password}
EOF
}
