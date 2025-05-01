DROP TABLE IF EXISTS website_review;

CREATE TABLE website_review (
    id CHAR(32) NOT NULL PRIMARY KEY,
    service VARCHAR(50) NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME(6) NOT NULL,
    user_id CHAR(32) NOT NULL,
    CONSTRAINT website_review_user_service_unique UNIQUE (user_id, service),
    CONSTRAINT website_review_user_id_fk FOREIGN KEY (user_id) REFERENCES website_user (id) ON DELETE CASCADE
); 