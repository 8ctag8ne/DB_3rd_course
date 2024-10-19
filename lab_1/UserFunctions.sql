USE AnimeDB;
GO

-- 1. Функція для отримання аніме за жанром
CREATE FUNCTION GetAnimeByGenre (@GenreName NVARCHAR(50))
RETURNS TABLE
AS
RETURN
(
    SELECT a.id, a.title, a.year
    FROM Anime a
    JOIN AnimeGenre ag ON a.id = ag.anime_id
    JOIN Genre g ON ag.genre_id = g.id
    WHERE g.name LIKE '%' + @GenreName + '%'
);
GO

-- 2. Функція для підрахунку кількості аніме за студією
CREATE FUNCTION CountAnimeByStudio (@StudioName NVARCHAR(100))
RETURNS INT
AS
BEGIN
    DECLARE @AnimeCount INT;
    SELECT @AnimeCount = COUNT(*)
    FROM Anime a
    JOIN AnimeStudio ass ON a.id = ass.anime_id
    JOIN Studio s ON ass.studio_id = s.id
    WHERE s.name LIKE '%' + @StudioName + '%';
    RETURN @AnimeCount;
END;
GO

-- 3. Функція для отримання середнього рейтингу аніме
CREATE FUNCTION GetAverageAnimeRating (@AnimeId INT)
RETURNS DECIMAL(3,2)
AS
BEGIN
    DECLARE @AvgRating DECIMAL(3,2);
    SELECT @AvgRating = AVG(CAST(rating AS DECIMAL(3,2)))
    FROM Review
    WHERE anime_id = @AnimeId;
    RETURN @AvgRating;
END;
GO

-- 4. Функція для отримання списку персонажів аніме
CREATE FUNCTION GetAnimeCharacters (@AnimeId INT)
RETURNS TABLE
AS
RETURN
(
    SELECT c.id, c.name, c.role
    FROM Character c
    WHERE c.anime_id = @AnimeId AND c.is_deleted = 0
);
GO

-- 5. Функція для отримання кількості переглядів аніме користувачами
CREATE FUNCTION GetAnimeWatchCount (@AnimeId INT)
RETURNS INT
AS
BEGIN
    DECLARE @WatchCount INT;
    SELECT @WatchCount = COUNT(*)
    FROM WatchStatus
    WHERE anime_id = @AnimeId AND status = 'Completed';
    RETURN @WatchCount;
END;
GO

-- 6. Функція для отримання списку аніме за роком випуску
CREATE FUNCTION GetAnimeByYear (@Year INT)
RETURNS TABLE
AS
RETURN
(
    SELECT id, title, episodes
    FROM Anime
    WHERE year = @Year AND is_deleted = 0
);
GO

-- 7. Функція для отримання топ-N аніме за рейтингом
CREATE FUNCTION GetTopRatedAnime (@N INT)
RETURNS TABLE
AS
RETURN
(
    SELECT TOP (@N) a.id, a.title, AVG(CAST(r.rating AS DECIMAL(3,2))) AS avg_rating
    FROM Anime a
    JOIN Review r ON a.id = r.anime_id
    GROUP BY a.id, a.title
    ORDER BY avg_rating DESC
);
GO

-- 8. Функція для отримання кількості постів на форумі для аніме
CREATE FUNCTION GetAnimeForumPostCount (@AnimeId INT)
RETURNS INT
AS
BEGIN
    DECLARE @PostCount INT;
    SELECT @PostCount = COUNT(*)
    FROM ForumThread ft
    JOIN ForumPost fp ON ft.id = fp.thread_id
    WHERE ft.anime_id = @AnimeId;
    RETURN @PostCount;
END;
GO

-- 9. Функція для отримання списку саундтреків аніме
CREATE FUNCTION GetAnimeSoundtracks (@AnimeId INT)
RETURNS TABLE
AS
RETURN
(
    SELECT id, title, artist, type
    FROM Soundtrack
    WHERE anime_id = @AnimeId
);
GO

-- 10. Функція для отримання рекомендованих аніме на основі переглянутого
CREATE FUNCTION GetRecommendedAnime (@UserId INT)
RETURNS TABLE
AS
RETURN
(
    SELECT DISTINCT a.id, a.title
    FROM Anime a
    JOIN Recommendation r ON a.id = r.recommended_anime_id
    JOIN WatchStatus ws ON r.anime_id = ws.anime_id
    WHERE ws.user_id = @UserId AND ws.status = 'Completed'
    AND a.id NOT IN (
        SELECT anime_id
        FROM WatchStatus
        WHERE user_id = @UserId
    )
);
GO