USE AnimeDB;
GO

-- 1. Представлення для перегляду популярних аніме (з рейтингом вище 8)
CREATE OR ALTER VIEW PopularAnime AS
SELECT a.id, a.title, a.year, AVG(r.rating) AS average_rating, COUNT(r.id) AS review_count
FROM Anime a
JOIN Review r ON a.id = r.anime_id
WHERE a.is_deleted = 0
GROUP BY a.id, a.title, a.year
HAVING AVG(r.rating) > 8
GO

-- 2. Представлення для перегляду активних користувачів (які залишили відгук за останній місяць)
CREATE OR ALTER VIEW ActiveUsers AS
SELECT u.id, u.username, u.email, COUNT(r.id) AS recent_reviews
FROM Users u
JOIN Review r ON u.id = r.user_id
WHERE r.created_at >= DATEADD(MONTH, -1, GETDATE())
AND u.is_active = 1
GROUP BY u.id, u.username, u.email
GO

-- 3. Представлення для перегляду аніме з найбільшою кількістю персонажів
CREATE OR ALTER VIEW AnimeWithMostCharacters AS
SELECT TOP 10 a.id, a.title, COUNT(c.id) AS character_count
FROM Anime a
JOIN Character c ON a.id = c.anime_id
WHERE a.is_deleted = 0 AND c.is_deleted = 0
GROUP BY a.id, a.title
ORDER BY COUNT(c.id) DESC
GO

-- 4. Представлення для перегляду найактивніших студій (за кількістю випущених аніме за останні 5 років)
CREATE OR ALTER VIEW ActiveStudios AS
SELECT TOP 100 PERCENT s.id, s.name, COUNT(a.id) AS anime_count
FROM Studio s
JOIN AnimeStudio [as] ON s.id = [as].studio_id
JOIN Anime a ON [as].anime_id = a.id
WHERE a.year >= YEAR(GETDATE()) - 5
AND s.is_deleted = 0 AND a.is_deleted = 0
GROUP BY s.id, s.name
HAVING COUNT(a.id) > 1
ORDER BY COUNT(a.id) DESC
GO

-- 5. Представлення для перегляду аніме з найбільшою кількістю обговорень на форумі
CREATE OR ALTER VIEW MostDiscussedAnime AS
SELECT TOP 20 a.id, a.title, COUNT(fp.id) AS post_count
FROM Anime a
JOIN ForumThread ft ON a.id = ft.anime_id
JOIN ForumPost fp ON ft.id = fp.thread_id
WHERE a.is_deleted = 0
GROUP BY a.id, a.title
ORDER BY COUNT(fp.id) DESC
GO