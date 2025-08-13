CREATE TABLE user_data (
    user_id VARCHAR(255) PRIMARY KEY,
    uploaded_notes INTEGER NOT NULL DEFAULT 0,
    last_query_date DATE,
    total_queries INTEGER NOT NULL DEFAULT 0,
    remaining_tokens INTEGER NOT NULL DEFAULT 1000
);
