USE AnimeDB;
GO

-- ��������� ��� �'����� ��������� Anime
CREATE PROCEDURE SoftDeleteAnime
    @AnimeId INT,
    @UpdatedBy INT
AS
BEGIN
    UPDATE Anime
    SET is_deleted = 1,
        updated_at = GETDATE(),
        updated_by = @UpdatedBy
    WHERE id = @AnimeId;
END
GO

-- ��������� ��� �'����� ��������� Studio
CREATE PROCEDURE SoftDeleteStudio
    @StudioId INT
AS
BEGIN
    UPDATE Studio
    SET is_deleted = 1
    WHERE id = @StudioId;
END
GO

-- ��������� ��� �'����� ��������� Character
CREATE PROCEDURE SoftDeleteCharacter
    @CharacterId INT,
    @UpdatedBy INT
AS
BEGIN
    UPDATE Character
    SET is_deleted = 1,
        updated_at = GETDATE(),
        updated_by = @UpdatedBy
    WHERE id = @CharacterId;
END
GO

-- ������ ��� ���������� ��������� ��������� Anime
CREATE TRIGGER PreventAnimeDelete
ON Anime
INSTEAD OF DELETE
AS
BEGIN
    RAISERROR('Physical deletion of Anime is not allowed. Use SoftDeleteAnime procedure instead.', 16, 1);
    ROLLBACK TRANSACTION;
END
GO

-- ������ ��� ���������� ��������� ��������� Studio
CREATE TRIGGER PreventStudioDelete
ON Studio
INSTEAD OF DELETE
AS
BEGIN
    RAISERROR('Physical deletion of Studio is not allowed. Use SoftDeleteStudio procedure instead.', 16, 1);
    ROLLBACK TRANSACTION;
END
GO

-- ������ ��� ���������� ��������� ��������� Character
CREATE TRIGGER PreventCharacterDelete
ON Character
INSTEAD OF DELETE
AS
BEGIN
    RAISERROR('Physical deletion of Character is not allowed. Use SoftDeleteCharacter procedure instead.', 16, 1);
    ROLLBACK TRANSACTION;
END
GO

-- ��������� ��� ���������� �'��� ���������� Anime
CREATE PROCEDURE RestoreAnime
    @AnimeId INT,
    @UpdatedBy INT
AS
BEGIN
    UPDATE Anime
    SET is_deleted = 0,
        updated_at = GETDATE(),
        updated_by = @UpdatedBy
    WHERE id = @AnimeId;
END
GO

-- ��������� ��� ���������� �'��� ���������� Studio
CREATE PROCEDURE RestoreStudio
    @StudioId INT
AS
BEGIN
    UPDATE Studio
    SET is_deleted = 0
    WHERE id = @StudioId;
END
GO

-- ��������� ��� ���������� �'��� ���������� Character
CREATE PROCEDURE RestoreCharacter
    @CharacterId INT,
    @UpdatedBy INT
AS
BEGIN
    UPDATE Character
    SET is_deleted = 0,
        updated_at = GETDATE(),
        updated_by = @UpdatedBy
    WHERE id = @CharacterId;
END
GO