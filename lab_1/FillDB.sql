USE AnimeDB;
GO

-- Insert sample data into Users table
INSERT INTO Users (username, email, password_hash, last_login, is_active)
VALUES 
('john_doe', 'john@example.com', 'hashed_password_1', GETDATE(), 1),
('jane_smith', 'jane@example.com', 'hashed_password_2', GETDATE(), 1),
('bob_johnson', 'bob@example.com', 'hashed_password_3', GETDATE(), 1);

-- Insert sample data into Anime table
INSERT INTO Anime (title, original_title, year, synopsis, episodes, duration, updated_by)
VALUES 
('Death Note', 'デスノート', 2006, 'A high school student discovers a supernatural notebook that allows him to kill anyone by writing the victim''s name while picturing their face.', 37, 23, 1),
('Attack on Titan', '進撃の巨人', 2013, 'In a world where humanity lives inside cities surrounded by enormous walls due to the Titans, gigantic humanoid creatures who devour humans seemingly without reason, a young boy named Eren Yeager vows to cleanse the earth of the Titans and restore mankind''s freedom.', 75, 24, 2),
('My Hero Academia', '僕のヒーローアカデミア', 2016, 'In a world where people with superpowers (known as "Quirks") are the norm, a boy without powers dreams of enrolling in a prestigious hero academy and learning what it really means to be a hero.', 113, 24, 3);

-- Insert sample data into Genre table
INSERT INTO Genre (name, description)
VALUES 
('Action', 'Emphasizes physical challenges, including fights, chases, and explosions.'),
('Mystery', 'Focuses on solving a crime or puzzle.'),
('Sci-Fi', 'Explores futuristic and scientific themes.');

-- Insert sample data into Studio table
INSERT INTO Studio (name, country, founded)
VALUES 
('Madhouse', 'Japan', '1972-10-17'),
('Wit Studio', 'Japan', '2012-06-01'),
('Bones', 'Japan', '1998-10-01');

-- Insert sample data into Character table
INSERT INTO Character (name, japanese_name, description, anime_id, role)
VALUES 
('Light Yagami', '夜神月', 'The main protagonist of Death Note, a brilliant but bored high school student who finds the Death Note.', 1, 'Protagonist'),
('Eren Yeager', 'エレン・イェーガー', 'The main protagonist of Attack on Titan, a young man who swears vengeance on enormous creatures that devoured his mother.', 2, 'Protagonist'),
('Izuku Midoriya', '緑谷出久', 'The main protagonist of My Hero Academia, a boy born without a Quirk in a world where they are the norm.', 3, 'Protagonist');

-- Insert sample data into VoiceActor table
INSERT INTO VoiceActor (name, birth_date, nationality)
VALUES 
('Mamoru Miyano', '1983-06-08', 'Japanese'),
('Yuki Kaji', '1985-09-03', 'Japanese'),
('Daiki Yamashita', '1989-07-07', 'Japanese');

-- Insert sample data into Staff table
INSERT INTO Staff (name, role, anime_id)
VALUES 
('Tetsuro Araki', 'Director', 1),
('Tetsuro Araki', 'Director', 2),
('Kenji Nagasaki', 'Director', 3);

-- Insert sample data into Review table
INSERT INTO Review (anime_id, user_id, rating, content)
VALUES 
(1, 1, 9, 'A masterpiece of psychological thriller anime!'),
(2, 2, 10, 'Epic story with amazing action scenes.'),
(3, 3, 8, 'Great superhero anime with lovable characters.');

-- Insert sample data into WatchStatus table
INSERT INTO WatchStatus (user_id, anime_id, status, episodes_watched, last_watched)
VALUES 
(1, 1, 'Completed', 37, GETDATE()),
(2, 2, 'Watching', 50, GETDATE()),
(3, 3, 'Planning', 0, NULL);

-- Insert sample data into Episode table
INSERT INTO Episode (anime_id, episode_number, title, air_date)
VALUES 
(1, 1, 'Rebirth', '2006-10-03'),
(2, 1, 'To You, 2000 Years in the Future', '2013-04-07'),
(3, 1, 'Izuku Midoriya: Origin', '2016-04-03');

-- Insert sample data into Soundtrack table
INSERT INTO Soundtrack (anime_id, title, artist, type)
VALUES 
(1, 'The World', 'Nightmare', 'Opening'),
(2, 'Guren no Yumiya', 'Linked Horizon', 'Opening'),
(3, 'The Day', 'Porno Graffitti', 'Opening');

-- Insert sample data into Merchandise table
INSERT INTO Merchandise (anime_id, name, type, price, stock)
VALUES 
(1, 'Death Note Replica', 'Collectible', 29.99, 100),
(2, 'Survey Corps Jacket', 'Clothing', 59.99, 50),
(3, 'All Might Figure', 'Figure', 39.99, 75);

-- Insert sample data into Award table
INSERT INTO Award (anime_id, name, year, category)
VALUES 
(1, 'Tokyo Anime Award', 2007, 'Best TV Anime'),
(2, 'Newtype Anime Awards', 2013, 'Best Work'),
(3, 'Crunchyroll Anime Awards', 2017, 'Anime of the Year');

-- Insert sample data into Recommendation table
INSERT INTO Recommendation (user_id, anime_id, recommended_anime_id)
VALUES 
(1, 1, 2),
(2, 2, 3),
(3, 3, 1);

-- Insert sample data into ForumThread table
INSERT INTO ForumThread (anime_id, user_id, title, content, views)
VALUES 
(1, 1, 'Death Note Ending Discussion', 'What did you think about the ending of Death Note? Let''s discuss!', 100),
(2, 2, 'Best Fight Scenes in AoT', 'Which fight scene in Attack on Titan is your favorite?', 150),
(3, 3, 'Favorite My Hero Academia Character?', 'Who is your favorite character in My Hero Academia and why?', 120);

-- Insert sample data into ForumPost table
INSERT INTO ForumPost (thread_id, user_id, content)
VALUES 
(1, 2, 'I thought the ending was brilliant. It really showed how absolute power corrupts absolutely.'),
(2, 3, 'The fight between Levi and the Beast Titan was incredible! The animation was top-notch.'),
(3, 1, 'All Might is my favorite. His sense of justice and his mentor role to Deku is inspiring.');

-- Insert sample data into many-to-many relationship tables
INSERT INTO AnimeGenre (anime_id, genre_id)
VALUES 
(1, 2), -- Death Note is Mystery
(2, 1), -- Attack on Titan is Action
(3, 1); -- My Hero Academia is Action

INSERT INTO AnimeStudio (anime_id, studio_id)
VALUES 
(1, 1), -- Death Note by Madhouse
(2, 2), -- Attack on Titan by Wit Studio
(3, 3); -- My Hero Academia by Bones

INSERT INTO CharacterVoiceActor (character_id, voice_actor_id, anime_id)
VALUES 
(1, 1, 1), -- Light Yagami voiced by Mamoru Miyano in Death Note
(2, 2, 2), -- Eren Yeager voiced by Yuki Kaji in Attack on Titan
(3, 3, 3); -- Izuku Midoriya voiced by Daiki Yamashita in My Hero Academia