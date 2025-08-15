```
terraform/
 ├─ main.tf          # Provider、VM、DB、Redis、S3 / MinIO
 ├─ docker.tf        # Docker container 定義
 ├─ secrets.tf       # Secret 管理
 ├─ variables.tf     # 所有變數
 └─ outputs.tf       # 輸出 endpoint / ports

```

- 查看 Terraform state 裡有哪些資源
`terraform state list`
| 工具             | 連線方式                          | 重要說明                                                          |
| -------------- | ----------------------------- | ------------------------------------------------------------- |
| Docker Compose | 用 **service name** (`redis`)  | network hostname 預設是 service name，如果指定 `container_name`，也可以用它 |
| Terraform      | 用 **container name** (`name`) | network hostname = container name，沒有 service name 概念          |
