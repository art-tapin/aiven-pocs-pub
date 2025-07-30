-- Teardown script for Bookstore Recommendations Demo
-- Removes all demo data and cleans up the database

-- Drop all data from tables
TRUNCATE TABLE ratings CASCADE;
TRUNCATE TABLE books CASCADE;

-- Reset sequences
ALTER SEQUENCE books_id_seq RESTART WITH 1;

-- Verify cleanup
SELECT 'Books count: ' || COUNT(*) as books_remaining FROM books;
SELECT 'Ratings count: ' || COUNT(*) as ratings_remaining FROM ratings; 