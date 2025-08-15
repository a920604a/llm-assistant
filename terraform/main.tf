terraform {
  required_version = ">= 1.5.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.21"
    }
    local = {
      source = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# 資料資料夾
resource "local_file" "data_dirs" {
  for_each = toset(["./data/note_db", "./data/note-storage", "./data/open-webui", "./data/qdrant_data"])
  filename = each.key
  content  = ""
}
