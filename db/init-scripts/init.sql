CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    last_query_date DATE,
    total_queries INTEGER NOT NULL DEFAULT 0,
    remaining_tokens INTEGER NOT NULL DEFAULT 1000
);

CREATE TABLE user_setting (
    user_id VARCHAR(255) PRIMARY KEY,
    user_language VARCHAR(255) NOT NULL,
    translate BOOLEAN NOT NULL DEFAULT FALSE,
    system_prompt TEXT NOT NULL DEFAULT '',
    top_k INTEGER NOT NULL DEFAULT 5,
    use_rag BOOLEAN NOT NULL DEFAULT TRUE,
    subscribe_email BOOLEAN NOT NULL DEFAULT FALSE,
    reranker_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    temperature FLOAT NOT NULL DEFAULT 0.6, -- LLM temperature
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    input_token INT,
    output_token INT,
    latency_ms INT, -- 延遲時間
    model VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 可以加索引加速查詢
CREATE INDEX idx_chat_history_user_id ON chat_history (user_id);

CREATE INDEX idx_chat_history_created_at ON chat_history (created_at);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL,
    upload_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255) NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    arxiv_id VARCHAR(32) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT[] NOT NULL,
    abstract TEXT,
    categories TEXT[],
    published_date DATE,
    updated_date DATE,
    pdf_url TEXT,
    pdf_cached_path TEXT,
    pdf_downloaded BOOLEAN DEFAULT FALSE,
    pdf_parsed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 可加索引，加速查詢
CREATE INDEX idx_papers_published_date ON papers (published_date);

CREATE INDEX idx_papers_categories ON papers USING GIN (categories);
