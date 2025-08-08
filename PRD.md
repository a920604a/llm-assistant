以下是根據你提出的 LLM 搜尋平台需求所擬定的專案需求書草案，涵蓋前端功能、後端流程、架構設計與模組劃分，方便你日後擴充或交接。

---

# 🔍 **RAG 教學筆記搜尋平台專案需求書**

## 🧾 專案名稱

> LLM 教學筆記搜尋平台（RAG + Qdrant + Ollama + React）

---

## 🎯 專案目標

建立一套前後端整合的 AI 教學筆記搜尋平台，使用者可上傳教學筆記（Markdown 檔案或整個資料夾），後端將其翻譯成中文、分段、向量化後存入向量資料庫（Qdrant）。使用者可輸入自然語言問題進行搜尋，透過 LLM 提供高相關且可追溯的回應與筆記片段。

---

## 🔧 技術選型

### 📦 後端

| 技術                                       | 說明                                    |
| ---------------------------------------- | ------------------------------------- |
| Python                                   | 主程式語言                                 |
| FastAPI                                  | RESTful API 建立                        |
| Ollama API                               | 調用 LLM 模型做翻譯與 Query Rewrite           |
| Qdrant                                   | 向量資料庫，用於儲存向量與 metadata                |
| SentenceTransformers or Ollama embedding | 用於文字向量化                               |
| Markdown parser                          | 支援檔案分段（例如 `mistune`、`markdown-it-py`） |

### 🌐 前端

| 技術                 | 說明                            |
| ------------------ | ----------------------------- |
| React (TypeScript) | 主架構                           |
| Tailwind CSS       | UI 樣式                         |
| Zustand / Redux    | 狀態管理                          |
| SWR / React Query  | API 資料擷取                      |
| File Upload Lib    | 上傳檔案與資料夾（例如 `react-dropzone`） |

---

## 📁 系統架構圖

```plaintext
[使用者]
   |
   ▼
[React 前端]
   |
   ▼
[FastAPI 後端]
   |
   ├── 上傳處理器（解析 Markdown + 翻譯 + 分段）
   ├── 向量化處理器（embedding + metadata）
   ├── Qdrant 儲存器（向量與屬性）
   └── 搜尋處理器（Query Rewrite + Hybrid Search + Rerank + Prompt）
   |
   ▼
[Qdrant 向量資料庫]
```

---

## ⚙️ 系統功能模組

### 🖼 前端功能模組

| 功能             | 描述                                 |
| -------------- | ---------------------------------- |
| 🔼 上傳教學筆記      | 支援單檔 .md 或整個資料夾拖拉上傳                |
| 📂 檔案預覽與解析     | 顯示 Markdown 內容，提供上傳結果狀態            |
| 🔍 問題查詢輸入      | 使用者可輸入問題，自然語言搜尋筆記內容                |
| 📘 搜尋結果回應      | 顯示來自 LLM 的回答與相關筆記片段                |
| 🧠 顯示回應來源      | 提供每段回答的原始筆記連結或上下文                  |
| 📊 搜尋過程視覺化（可選） | 顯示 query rewrite、reranking 結果等中繼資料 |

---

### 🔁 後端處理流程（pipeline）

#### 1️⃣ 筆記上傳流程

```plaintext
[接收檔案] → [Markdown 解析與分段] → [翻譯中文 (Ollama)] → [文字向量化] → [建立 metadata] → [插入 Qdrant]
```

* **翻譯工具**：Ollama (e.g., `llama3`, `mistral`)
* **分段規則**：標題段落分群、段落合併避免過短（chunk size 控制）
* **metadata 結構**：

  ```json
  {
    "source": "filename.md",
    "section_title": "章節標題",
    "translated": "段落內容翻譯",
    "tags": ["function", "python", "loop"]
  }
  ```

#### 2️⃣ 搜尋流程

```plaintext
[使用者輸入問題]
  ↓
[Query Rewrite - LLM 改寫查詢]
  ↓
[Hybrid Search - Qdrant 向量 + Filter]
  ↓
[Document Reranking - LLM or Embedding Score]
  ↓
[Prompt 構建 - 建立上下文 Prompt]
  ↓
[LLM 回答生成 - Ollama API 呼叫]
  ↓
[回傳回答 + 關聯筆記]
```

---

## 📌 功能細節說明

### 上傳

* 支援：

  * 單一 .md
  * 整個資料夾（透過遞迴抓取所有 `.md` 檔）
* 後端接收：

  * 儲存原始筆記（可選）
  * 執行翻譯（英文→中文）
  * 切 chunk + embedding
  * 為每段生成屬性資料（metadata）

### 搜尋

* Query Rewrite：

  * 利用 Ollama LLM 改寫查詢，加強語意匹配
* Hybrid Search：

  * Qdrant 同時用向量＋metadata（如標題、tags）做過濾
  * 支援文字 keyword filter 或 top-k 向量檢索
* Reranking：

  * 使用 LLM 比對 query 與 chunk 對應程度進行 rerank
* Prompt 構建：

  * 建立具脈絡的 prompt 給 LLM 回答問題
* 回傳結果：

  * 包含 LLM 回答 + 所引用的段落（標示來源）

---

## 🗃 資料結構設計

```ts
// 每個筆記段落的資料結構
type NoteChunk = {
  id: string
  text: string
  translated: string
  vector: number[]
  metadata: {
    file: string
    section: string
    tags?: string[]
    created_at: string
  }
}
```

---

## 📤 API 設計

| 路由               | 方法   | 說明            |
| ---------------- | ---- | ------------- |
| `/upload`        | POST | 上傳筆記（支援單檔與多檔） |
| `/search`        | POST | 輸入問題後進行全文查詢   |
| `/status`        | GET  | 查詢筆記處理進度狀態    |
| `/documents`     | GET  | 已上傳文件清單       |
| `/documents/:id` | GET  | 單一文件內容與摘要     |

---

## 🔐 權限與安全（進階可擴充）

* 使用者登入（可用 Firebase Auth / Magic Link）
* 每位使用者有獨立的 Qdrant collection / 分區
* 向量資料不可共用除非授權

---

## 📈 未來可擴充功能

* ✅ 回答後可「點選來源筆記段落」
* ✅ 加入「收藏筆記」或「摘要筆記」功能
* ✅ 使用者可以「修正翻譯結果」
* ✅ 上傳 PDF → 自動轉 Markdown
* ✅ 自訂 Prompt 模板或 QA 類型（如考試題庫、課程摘要）

---

## ✅ 開發時程建議（簡化版）

| 時間     | 目標                                   |
| ------ | ------------------------------------ |
| Week 1 | 架構設計與 Qdrant 向量 DB 建立測試              |
| Week 2 | 完成上傳 + 翻譯 + 切段 + 向量化 pipeline        |
| Week 3 | 完成前端筆記上傳與顯示功能                        |
| Week 4 | 實作搜尋流程（Query Rewrite + Qdrant + LLM） |
| Week 5 | 前端搜尋輸入與顯示整合、優化 UI                    |
| Week 6 | 部署測試、效能優化與 bug 修復                    |

---
