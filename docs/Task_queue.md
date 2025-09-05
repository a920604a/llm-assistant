

---

## **訊息任務處理生態系**

---

## 整體脈絡

* **核心問題**：如何把「要做的工作（任務）」從**產生方**（Producer）送給**處理方**（Consumer/Worker），並且在過程中能排程、重試、分散處理。
* **解決方式**：透過 **Broker**（訊息中介系統）來解耦生產與消費。

---

## 名詞區分

### 1. Celery

* **定位**：一個 Python 的分散式任務隊列框架。
* **功能**：

  * 定義任務（tasks）
  * 排程（beat）
  * 執行（worker）
  * 支援 Broker（如 Redis、RabbitMQ、Kafka）
* **你可以把它當成「任務管理員」**。

---

### 2. Broker

* **定位**：負責「訊息傳遞」的中介（像郵局）。
* **例子**：

  * Redis
  * RabbitMQ
  * Kafka
* **Celery 本身不處理訊息傳送，它一定需要一個 broker。**

---

### 3. Beat

* **定位**：Celery 內建的**排程器**。
* **用途**：像 cron job，一段時間送一次任務到 Broker，然後 Worker 執行。
* **例子**：

  * 每天 8 點寄 email 報表 → beat 發出「寄信任務」 → broker → worker 執行。

---

### 4. Worker

* **定位**：真正執行任務的工人程式。
* **功能**：從 broker 拿到任務 → 執行 → 回傳結果（可存到 backend）。

---

### 5. Producer

* **定位**：產生任務的人（程式）。
* **功能**：呼叫 Celery task → 寫入 broker → 等 worker 執行。
* **例子**：

  * Web API 收到「寄信請求」 → 呼叫 `task.send_email.delay(...)` → Celery 把任務丟給 broker。

---

### 6. Consumer

* **定位**：任務的消費者。
* **在 Celery 裡就是 worker**。
* **Worker = Consumer**。

---

### 7. Kafka

* **定位**：一個高效能、分散式的訊息隊列系統（broker 的一種）。
* **差異**：

  * RabbitMQ / Redis：比較適合任務佇列（queue）模式。
  * Kafka：偏向事件流（event streaming），可以讓很多 consumer 同時訂閱，不會只被「一個工人」拿走。

---

## 串起來的例子

1. **Producer**：Web API → 發出「寄信任務」
2. **Broker**：Redis / RabbitMQ / Kafka → 暫存任務
3. **Beat**（可選）：如果是排程任務，由它產生 → 丟給 broker
4. **Worker/Consumer**：Celery worker → 從 broker 拿任務 → 執行 → 存結果

---

👉 簡單比喻：

* **Producer**：寄件人
* **Broker**：郵局（信件分發）
* **Consumer/Worker**：收件人（工人去做事）
* **Beat**：定時寄信人
* **Celery**：一個整合寄件、排程、收件的「任務郵務系統」
* **Kafka**：一種超強郵局，信可以被很多人抄送。


```mermaid
flowchart LR
    subgraph App["應用程式 (Producer)"]
        A[呼叫 Celery Task <br/> e.g. send_email.delay]
    end

    subgraph Redis["Broker (Redis)"]
        Q[(Task Queue)]
    end

    subgraph Celery["Celery Worker (Consumer)"]
        W1[Worker 1]
        W2[Worker 2]
    end

    A -- 發任務 --> Q
    Q -- 分發任務 --> W1
    Q -- 分發任務 --> W2

```

```mermaid
flowchart LR

    %% ===== Storage 模塊 =====
    subgraph Storage["Storage 模塊 (資料存取)"]
        note_db[Postgres<br/>關聯式資料庫]:::storage
        note_storage[MinIO<br/>物件存儲]:::storage
        note_qdrant[Qdrant<br/>向量資料庫]:::storage
    end

    %% Flower 與 Redis 共用
    redis[Redis 任務隊列]:::queue

    %% ===== Ingest Arxiv TaskWorker =====
    subgraph TaskWorker1["Ingest Arxiv Paper 任務隊列與後台處理"]
        worker[Worker<br/>執行 Celery 任務]:::worker
        beat[Beat<br/>定時任務發送]:::beat

    end
    %% 任務流程
    beat -->|定時任務推送到 Redis| redis
    redis -->|Worker 從 Redis 拉取任務| worker

    %% ===== Email Service TaskWorker =====
    subgraph TaskWorker2["Email Service 任務隊列與後台處理"]
        worker2[Worker<br/>執行 Celery 任務]:::worker
        beat2[Beat<br/>定時任務發送]:::beat


    end


    %% 任務流程
    beat2 -->|定時任務推送到 Redis| redis
    redis -->|Worker 從 Redis 拉取任務| worker2

    worker -->|任務完成結果存入 Storage| Storage
    worker2 -->|任務完成結果存入 Storage| Storage

    worker2 -->|寄信給使用者| User


    %% ===== 模塊顏色 =====
    classDef user fill:#FFD700,stroke:#333,stroke-width:1px
    classDef frontend fill:#87CEEB,stroke:#333,stroke-width:1px
    classDef auth fill:#FFA500,stroke:#333,stroke-width:1px
    classDef service fill:#7FFFD4,stroke:#333,stroke-width:1px
    classDef storage fill:#F08080,stroke:#333,stroke-width:1px
    classDef worker fill:#9370DB,stroke:#333,stroke-width:1px
    classDef beat fill:#BA55D3,stroke:#333,stroke-width:1px
    classDef queue fill:#40E0D0,stroke:#333,stroke-width:1px
    classDef monitor fill:#FFDAB9,stroke:#333,stroke-width:1px
    classDef llm fill:#90EE90,stroke:#333,stroke-width:1px

```
