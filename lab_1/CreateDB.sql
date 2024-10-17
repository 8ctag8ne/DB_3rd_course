-- Create database
CREATE DATABASE AnimeDB;
GO

USE AnimeDB;
GO

-- Create tables
CREATE TABLE Users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) NOT NULL,
    email NVARCHAR(100) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    last_login DATETIME,
    is_active BIT NOT NULL DEFAULT 1
);

CREATE TABLE Anime (
    id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(255) NOT NULL,
    original_title NVARCHAR(255),
    year INT,
    synopsis NVARCHAR(MAX),
    episodes INT,
    duration INT,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_by INT,
    FOREIGN KEY (updated_by) REFERENCES Users(id)
);

CREATE TABLE Genre (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX)
);

CREATE TABLE Studio (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    country NVARCHAR(50),
    founded DATE,
    is_deleted BIT NOT NULL DEFAULT 0
);

CREATE TABLE Character (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    japanese_name NVARCHAR(100),
    description NVARCHAR(MAX),
    anime_id INT,
    role NVARCHAR(50),
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_by INT,
    FOREIGN KEY (anime_id) REFERENCES Anime(id),
    FOREIGN KEY (updated_by) REFERENCES Users(id)
);

CREATE TABLE VoiceActor (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    birth_date DATE,
    nationality NVARCHAR(50)
);

CREATE TABLE Staff (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    role NVARCHAR(50),
    anime_id INT,
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);

CREATE TABLE Review (
    id INT PRIMARY KEY IDENTITY(1,1),
    anime_id INT,
    user_id INT,
    rating INT,
    content NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (anime_id) REFERENCES Anime(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE WatchStatus (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    anime_id INT,
    status NVARCHAR(20),
    episodes_watched INT,
    last_watched DATETIME,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);

CREATE TABLE Episode (
    id INT PRIMARY KEY IDENTITY(1,1),
    anime_id INT,
    episode_number INT,
    title NVARCHAR(255),
    air_date DATE,
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);

CREATE TABLE Soundtrack (
    id INT PRIMARY KEY IDENTITY(1,1),
    anime_id INT,
    title NVARCHAR(255) NOT NULL,
    artist NVARCHAR(100),
    type NVARCHAR(50),
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);

CREATE TABLE Merchandise (
    id INT PRIMARY KEY IDENTITY(1,1),
    anime_id INT,
    name NVARCHAR(255) NOT NULL,
    type NVARCHAR(50),
    price DECIMAL(10, 2),
    stock INT,
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);

CREATE TABLE Award (
    id INT PRIMARY KEY IDENTITY(1,1),
    anime_id INT,
    name NVARCHAR(255) NOT NULL,
    year INT,
    category NVARCHAR(100),
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);

CREATE TABLE Recommendation (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    anime_id INT,
    recommended_anime_id INT,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (anime_id) REFERENCES Anime(id),
    FOREIGN KEY (recommended_anime_id) REFERENCES Anime(id)
);

CREATE TABLE ForumThread (
    id INT PRIMARY KEY IDENTITY(1,1),
    anime_id INT,
    user_id INT,
    title NVARCHAR(255) NOT NULL,
    content NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    views INT DEFAULT 0,
    FOREIGN KEY (anime_id) REFERENCES Anime(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE ForumPost (
    id INT PRIMARY KEY IDENTITY(1,1),
    thread_id INT,
    user_id INT,
    content NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (thread_id) REFERENCES ForumThread(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Create many-to-many relationships
CREATE TABLE AnimeGenre (
    anime_id INT,
    genre_id INT,
    PRIMARY KEY (anime_id, genre_id),
    FOREIGN KEY (anime_id) REFERENCES Anime(id),
    FOREIGN KEY (genre_id) REFERENCES Genre(id)
);

CREATE TABLE AnimeStudio (
    anime_id INT,
    studio_id INT,
    PRIMARY KEY (anime_id, studio_id),
    FOREIGN KEY (anime_id) REFERENCES Anime(id),
    FOREIGN KEY (studio_id) REFERENCES Studio(id)
);

CREATE TABLE CharacterVoiceActor (
    character_id INT,
    voice_actor_id INT,
    anime_id INT,
    PRIMARY KEY (character_id, voice_actor_id, anime_id),
    FOREIGN KEY (character_id) REFERENCES Character(id),
    FOREIGN KEY (voice_actor_id) REFERENCES VoiceActor(id),
    FOREIGN KEY (anime_id) REFERENCES Anime(id)
);
