CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    last_query_date DATE,
    total_queries INTEGER NOT NULL DEFAULT 0,
    remaining_tokens INTEGER NOT NULL DEFAULT 1000
);


CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255) NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 可加索引，加速查詢
CREATE INDEX idx_papers_published_date ON papers(published_date);
CREATE INDEX idx_papers_categories ON papers USING GIN (categories);
