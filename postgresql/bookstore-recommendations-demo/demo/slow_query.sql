-- AI Insights Slow Query (Intentionally Inefficient)
-- This query uses database worst practices to ensure it runs slowly
-- and triggers AI Insights optimization suggestions

SELECT 
    b.title,
    AVG(r.rating) as avg_rating,
    COUNT(r.rating) as num_ratings,
    (SELECT COUNT(*) FROM ratings r2 WHERE r2.book_id = b.id) as total_ratings_for_book,
    (SELECT AVG(r3.rating) FROM ratings r3 WHERE r3.book_id = b.id) as book_avg_rating,
    (SELECT COUNT(*) FROM ratings r4 WHERE r4.book_id = b.id AND r4.rating >= 4) as high_ratings_count,
    (SELECT COUNT(*) FROM ratings r5 WHERE r5.book_id = b.id AND r5.rating <= 2) as low_ratings_count
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
WHERE r.rating > 2
AND EXISTS (
    SELECT 1 FROM ratings r2 
    WHERE r2.book_id = b.id 
    AND r2.rating >= 4
)
AND b.id IN (
    SELECT DISTINCT book_id FROM ratings 
    WHERE rating > 3
)
AND b.id IN (
    SELECT DISTINCT book_id FROM ratings 
    WHERE rating >= 4
)
GROUP BY b.id, b.title
HAVING COUNT(r.rating) >= 1
ORDER BY avg_rating DESC, num_ratings DESC, b.title ASC
LIMIT 20; 