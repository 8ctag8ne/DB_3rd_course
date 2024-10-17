USE AnimeDB;
GO

-- Спрощений тригер для відстеження оновлень в таблиці Anime
CREATE OR ALTER TRIGGER TrackAnimeUpdates
ON Anime
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE Anime
    SET updated_at = GETDATE(),
        updated_by = COALESCE(i.updated_by, d.updated_by)
    FROM Anime a
    INNER JOIN inserted i ON a.id = i.id
    INNER JOIN deleted d ON a.id = d.id;
END
GO

-- Спрощений тригер для відстеження оновлень в таблиці Character
CREATE OR ALTER TRIGGER TrackCharacterUpdates
ON Character
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE Character
    SET updated_at = GETDATE(),
        updated_by = COALESCE(i.updated_by, d.updated_by)
    FROM Character c
    INNER JOIN inserted i ON c.id = i.id
    INNER JOIN deleted d ON c.id = d.id;
END
GO

-- Спрощений тригер для відстеження оновлень в таблиці Review
CREATE OR ALTER TRIGGER TrackReviewUpdates
ON Review
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE Review
    SET updated_at = GETDATE()
    FROM Review r
    INNER JOIN inserted i ON r.id = i.id;
END
GO

-- Спрощений тригер для відстеження оновлень в таблиці ForumPost
CREATE OR ALTER TRIGGER TrackForumPostUpdates
ON ForumPost
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE ForumPost
    SET updated_at = GETDATE()
    FROM ForumPost fp
    INNER JOIN inserted i ON fp.id = i.id;
END
GO