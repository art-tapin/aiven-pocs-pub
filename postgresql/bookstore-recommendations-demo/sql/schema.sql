-- Enable pgvector extension for vector operations
-- Note: pgvector is enabled via SQL command
CREATE EXTENSION IF NOT EXISTS vector;

-- Create books table with vector embeddings
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    embedding VECTOR(1536)
);

-- Create ratings table for user book ratings
CREATE TABLE IF NOT EXISTS ratings (
    user_id INT,
    book_id INT REFERENCES books(id),
    rating SMALLINT CHECK (rating >= 1 AND rating <= 5),
    ts TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_books_embedding ON books USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_ratings_book_id ON ratings(book_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_ts ON ratings(ts); 