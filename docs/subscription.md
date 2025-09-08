
```mermaid
flowchart LR
  S[每日排程] e1@--> F[篩選訂閱用戶]
  F e2@--> G[Fetch paper]
  G e3@--> R[生成摘要]
  R e4@--> E[渲染 HTML Email]
  E e5@--> M[寄送]
  e1@{ animation: slow }
  e2@{ animation: fast }
  e3@{ animation: fast }
  e4@{ animation: fast }
  e5@{ animation: slow }
```
