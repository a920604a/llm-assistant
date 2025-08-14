variable "db_user" {
  type    = string
  default = "user"
}

variable "db_password" {
  type    = string
  default = "password"
}

variable "db_name" {
  type    = string
  default = "note"
}

variable "minio_user" {
  type    = string
  default = "note"
}

variable "minio_password" {
  type    = string
  default = "note123note123"
}

variable "webui_user" {
  type    = string
  default = "admin@example.com"
}

variable "webui_password" {
  type    = string
  default = "0961220102"
}
