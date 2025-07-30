-- AI Insights Optimized Query
-- Paste the optimized query from Aiven AI Insights here
-- This query will be benchmarked against the original slow query

SELECT 
    b.title,
    AVG(r.rating) as avg_rating,
    COUNT(r.rating) as num_ratings,
    (SELECT COUNT(*) FROM ratings r2 WHERE r2.book_id = b.id) as total_ratings_for_book,
    (SELECT AVG(r3.rating) FROM ratings r3 WHERE r3.book_id = b.id) as book_avg_rating,
    (SELECT COUNT(*) FROM ratings r4 WHERE r4.book_id = b.id AND r4.rating >= 4) as high_ratings_count,
    (SELECT COUNT(*) FROM ratings r5 WHERE r5.book_id = b.id AND r5.rating <= 2) as low_ratings_count
FROM books b
INNER JOIN ratings r ON b.id = r.book_id
WHERE r.rating > 2
AND b.id IN (
    SELECT r2.book_id FROM ratings r2 
    WHERE 1 = 1
    AND r2.rating >= 4
)
AND EXISTS (
    SELECT DISTINCT 1 FROM ratings 
    WHERE (
        "ratings".rating > 3
    )
    AND (
        b.id = ratings.book_id
    )
)
GROUP BY b.id, b.title
HAVING COUNT(r.rating) >= 1
ORDER BY avg_rating DESC, num_ratings DESC, b.title ASC
LIMIT 20; 
