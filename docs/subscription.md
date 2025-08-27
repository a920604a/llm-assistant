
```mermaid
flowchart LR
  S[每日排程] --> F[篩選訂閱用戶]
  F --> G[Fetch paper]
  G --> R[生成摘要]
  R --> E[渲染 HTML Email]
  E --> M[寄送]
```
