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
