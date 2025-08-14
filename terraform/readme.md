```
terraform/
 ├─ main.tf          # Provider、VM、DB、Redis、S3 / MinIO
 ├─ docker.tf        # Docker container 定義
 ├─ secrets.tf       # Secret 管理
 ├─ variables.tf     # 所有變數
 └─ outputs.tf       # 輸出 endpoint / ports

```