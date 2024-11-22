from typing import Dict

import pyodbc
import random
import string
import datetime

from performance_metrics import PerformanceMetrics, measure_execution_time


class MSSQLDatabase:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.performance_metrics = PerformanceMetrics()

    def _connect(self):
        """Підключення до бази даних."""
        return pyodbc.connect(self.connection_string)

    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        return self.performance_metrics.get_statistics()

    # READ операції
    @measure_execution_time
    def fetch_anime_simple(self, filters=None, limit=10):
        """Простий варіант читання записів з таблиці Anime."""
        query = "SELECT TOP {} * FROM Anime".format(limit)
        params = []
        if filters:
            filter_clauses = []
            for column, value in filters.items():
                if value is not None:
                    filter_clauses.append(f"{column} = ?")
                    params.append(value)
            if filter_clauses:
                query += " WHERE " + " AND ".join(filter_clauses)

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    @measure_execution_time
    def fetch_anime_with_relations(self, filters=None, limit=10):
        """Складний варіант читання записів з таблиці Anime з пов'язаними даними."""
        query = """
            SELECT TOP {} 
                a.*,
                STRING_AGG(CAST(g.id AS VARCHAR) + ':' + g.name, ';') as genres,
                STRING_AGG(CAST(r.id AS VARCHAR) + ':' + CAST(r.rating AS VARCHAR) + ':' + r.content, ';') as reviews
            FROM Anime a
            LEFT JOIN AnimeGenre ag ON a.id = ag.anime_id
            LEFT JOIN Genre g ON ag.genre_id = g.id
            LEFT JOIN Review r ON a.id = r.anime_id
        """.format(limit)

        params = []
        if filters:
            filter_clauses = []
            for column, value in filters.items():
                if value is not None:
                    filter_clauses.append(f"a.{column} = ?")
                    params.append(value)
            if filter_clauses:
                query += " WHERE " + " AND ".join(filter_clauses)

        query += " GROUP BY a.id, a.title, a.original_title, a.year, a.synopsis, a.episodes, " \
                 "a.duration, a.is_deleted, a.created_at, a.updated_at, a.updated_by"

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    # CREATE операції
    @measure_execution_time
    def insert_anime_simple(self, anime_data):
        """Простий варіант додавання запису в таблицю Anime."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Anime (title, original_title, year, synopsis, episodes, 
                                    duration, is_deleted, created_at, updated_at, updated_by)
                   OUTPUT INSERTED.id
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (anime_data['title'], anime_data['original_title'], anime_data['year'],
                 anime_data['synopsis'], anime_data['episodes'], anime_data['duration'],
                 anime_data.get('is_deleted', False),
                 datetime.datetime.now(), datetime.datetime.now(),
                 anime_data['updated_by'])
            )
            anime_id = cursor.fetchone()[0]
            conn.commit()
            return anime_id

    @measure_execution_time
    def insert_anime_with_relations(self, anime_data, genres, reviews):
        """Складний варіант додавання запису в таблицю Anime з пов'язаними даними."""
        with self._connect() as conn:
            cursor = conn.cursor()

            # Додаємо аніме
            anime_id = self.insert_anime_simple(anime_data)

            # Додаємо жанри
            for genre_id in genres:
                cursor.execute(
                    "INSERT INTO AnimeGenre (anime_id, genre_id) VALUES (?, ?)",
                    (anime_id, genre_id)
                )

            # Додаємо відгуки
            for review in reviews:
                cursor.execute(
                    """INSERT INTO Review 
                       (anime_id, user_id, rating, content, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (anime_id, review['user_id'], review['rating'],
                     review['content'], datetime.datetime.now(), datetime.datetime.now())
                )

            conn.commit()
            return anime_id

    # UPDATE операції
    @measure_execution_time
    def update_anime_simple(self, anime_id, updates):
        """Простий варіант оновлення запису в таблиці Anime."""
        with self._connect() as conn:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
            params = list(updates.values()) + [anime_id]
            cursor.execute(
                f"UPDATE Anime SET {set_clause} WHERE id = ?",
                params
            )
            conn.commit()

    @measure_execution_time
    def update_anime_with_relations(self, anime_id, anime_updates=None, genres=None, reviews=None):
        """Складний варіант оновлення запису в таблиці Anime з пов'язаними даними."""
        with self._connect() as conn:
            cursor = conn.cursor()

            # Оновлюємо основні дані аніме
            if anime_updates:
                self.update_anime_simple(anime_id, anime_updates)

            # Оновлюємо жанри
            if genres is not None:
                cursor.execute("DELETE FROM AnimeGenre WHERE anime_id = ?", (anime_id,))
                for genre_id in genres:
                    cursor.execute(
                        "INSERT INTO AnimeGenre (anime_id, genre_id) VALUES (?, ?)",
                        (anime_id, genre_id)
                    )

            # Оновлюємо відгуки
            if reviews is not None:
                cursor.execute("DELETE FROM Review WHERE anime_id = ?", (anime_id,))
                for review in reviews:
                    cursor.execute(
                        """INSERT INTO Review 
                           (anime_id, user_id, rating, content, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (anime_id, review['user_id'], review['rating'],
                         review['content'], datetime.datetime.now(), datetime.datetime.now())
                    )

            conn.commit()

    # DELETE операції
    @measure_execution_time
    def delete_anime_simple(self, anime_ids=None):
        """Простий варіант видалення записів з таблиці Anime."""
        with self._connect() as conn:
            cursor = conn.cursor()
            if anime_ids:
                query = "DELETE FROM Anime WHERE id IN ({})".format(",".join("?" for _ in anime_ids))
                cursor.execute(query, anime_ids)
            else:
                cursor.execute("DELETE FROM Anime")
            conn.commit()

    @measure_execution_time
    def delete_anime_with_relations(self, anime_ids=None):
        """Складний варіант видалення записів з таблиці Anime з пов'язаними даними."""
        with self._connect() as conn:
            cursor = conn.cursor()

            if anime_ids:
                # Видаляємо пов'язані відгуки
                query = "DELETE FROM Review WHERE anime_id IN ({})".format(",".join("?" for _ in anime_ids))
                cursor.execute(query, anime_ids)

                # Видаляємо пов'язані жанри
                query = "DELETE FROM AnimeGenre WHERE anime_id IN ({})".format(",".join("?" for _ in anime_ids))
                cursor.execute(query, anime_ids)

                # Видаляємо саме аніме
                query = "DELETE FROM Anime WHERE id IN ({})".format(",".join("?" for _ in anime_ids))
                cursor.execute(query, anime_ids)
            else:
                cursor.execute("DELETE FROM Review")
                cursor.execute("DELETE FROM AnimeGenre")
                cursor.execute("DELETE FROM Anime")

            conn.commit()

    # Допоміжні методи залишаються без змін
    def fetch_existing_genres(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT [id], [name] FROM [Genre]")
            return cursor.fetchall()

    def fetch_existing_users(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT [id] FROM [Users]")
            return [row[0] for row in cursor.fetchall()]

    def generate_entities(self, num_entities):
        """
        Генерує колекцію сутностей аніме з пов'язаними даними.

        Args:
            num_entities (int): кількість сутностей для генерації

        Returns:
            list: список словників, що містять дані аніме та пов'язані сутності
        """
        existing_genres = self.fetch_existing_genres()
        existing_users = self.fetch_existing_users()

        entities = []
        for _ in range(num_entities):
            # Основні дані аніме
            anime = {
                'title': ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20))),
                'original_title': ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20))),
                'year': random.randint(1900, 2024),
                'synopsis': '\n'.join([
                    ' '.join(random.choices(string.ascii_letters, k=random.randint(10, 50)))
                    for _ in range(random.randint(1, 5))
                ]),
                'episodes': random.randint(1, 100),
                'duration': random.randint(10, 120),
                'is_deleted': random.choice([True, False]),
                'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365)),
                'updated_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30)),
                'updated_by': random.choice(existing_users)
            }

            # Генерація пов'язаних жанрів
            genres = random.sample([g[0] for g in existing_genres], k=random.randint(1, min(5, len(existing_genres))))

            # Генерація відгуків
            reviews = []
            for _ in range(random.randint(1, 10)):
                review = {
                    'user_id': random.choice(existing_users),
                    'rating': random.randint(1, 10),
                    'content': ' '.join(random.choices(string.ascii_letters, k=random.randint(20, 100))),
                    'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365)),
                    'updated_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                }
                reviews.append(review)

            entities.append({
                'anime': anime,
                'genres': genres,
                'reviews': reviews
            })

        return entities

    @measure_execution_time
    @measure_execution_time
    def insert_entities_batch(self, entities, batch_size=100):
        """
        Оптимізована пакетна вставка аніме-сутностей з поліпшеною продуктивністю.

        Args:
            entities (list): список сутностей для вставки
            batch_size (int): розмір пакету для розбиття великих наборів даних
        """
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]

            with self._connect() as conn:
                cursor = conn.cursor()

                # Створення тимчасової таблиці для аніме
                cursor.execute("""
                    CREATE TABLE #TempAnime (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        title NVARCHAR(255),
                        original_title NVARCHAR(255),
                        year INT,
                        synopsis NTEXT,
                        episodes INT,
                        duration INT,
                        is_deleted BIT,
                        created_at DATETIME,
                        updated_at DATETIME,
                        updated_by NVARCHAR(100)
                    )
                """)

                # Підготовка даних для вставки
                anime_data = [
                    (
                        entity['anime']['title'],
                        entity['anime']['original_title'],
                        entity['anime']['year'],
                        entity['anime']['synopsis'],
                        entity['anime']['episodes'],
                        entity['anime']['duration'],
                        entity['anime'].get('is_deleted', False),
                        entity['anime']['created_at'],
                        entity['anime']['updated_at'],
                        entity['anime']['updated_by']
                    ) for entity in batch
                ]

                # Вставка аніме у тимчасову таблицю
                anime_insert_query = """
                INSERT INTO #TempAnime 
                (title, original_title, year, synopsis, episodes, duration, 
                is_deleted, created_at, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.executemany(anime_insert_query, anime_data)

                # Вставка аніме з тимчасової таблиці в основну з отриманням ID
                cursor.execute("""
                INSERT INTO Anime 
                (title, original_title, year, synopsis, episodes, duration, 
                is_deleted, created_at, updated_at, updated_by)
                OUTPUT INSERTED.id, INSERTED.title
                SELECT title, original_title, year, synopsis, episodes, duration, 
                is_deleted, created_at, updated_at, updated_by
                FROM #TempAnime
                """)
                inserted_anime = cursor.fetchall()

                # Пакетна вставка жанрів
                genre_data = []
                for idx, entity in enumerate(batch):
                    anime_id = inserted_anime[idx][0]
                    genre_data.extend([(anime_id, genre_id) for genre_id in entity['genres']])

                if genre_data:
                    genre_insert_query = """
                    INSERT INTO AnimeGenre (anime_id, genre_id)
                    VALUES (?, ?)
                    """
                    cursor.executemany(genre_insert_query, genre_data)

                # Пакетна вставка оглядів
                review_data = []
                for idx, entity in enumerate(batch):
                    anime_id = inserted_anime[idx][0]
                    review_data.extend([
                        (
                            anime_id,
                            review['user_id'],
                            review['rating'],
                            review['content'],
                            review['created_at'],
                            review['updated_at']
                        ) for review in entity['reviews']
                    ])

                if review_data:
                    review_insert_query = """
                    INSERT INTO Review 
                    (anime_id, user_id, rating, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cursor.executemany(review_insert_query, review_data)

                # Видалення тимчасової таблиці
                cursor.execute("DROP TABLE #TempAnime")

                conn.commit()

    @measure_execution_time
    def insert_entities_batch_simple(self, entities, batch_size=100):
        """
        Оптимізована пакетна вставка аніме-сутностей без пов'язаних даних.

        Args:
            entities (list): список сутностей для вставки
            batch_size (int): розмір пакету для розбиття великих наборів даних
        """
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]

            with self._connect() as conn:
                cursor = conn.cursor()

                # Створення тимчасової таблиці для аніме
                cursor.execute("""
                    CREATE TABLE #TempAnime (
                        title NVARCHAR(255),
                        original_title NVARCHAR(255),
                        year INT,
                        synopsis NTEXT,
                        episodes INT,
                        duration INT,
                        is_deleted BIT,
                        created_at DATETIME,
                        updated_at DATETIME,
                        updated_by NVARCHAR(100)
                    )
                """)

                # Підготовка даних для вставки
                anime_data = [
                    (
                        entity['anime']['title'],
                        entity['anime']['original_title'],
                        entity['anime']['year'],
                        entity['anime']['synopsis'],
                        entity['anime']['episodes'],
                        entity['anime']['duration'],
                        entity['anime'].get('is_deleted', False),
                        entity['anime']['created_at'],
                        entity['anime']['updated_at'],
                        entity['anime']['updated_by']
                    ) for entity in batch
                ]

                # Вставка аніме у тимчасову таблицю
                anime_insert_query = """
                INSERT INTO #TempAnime 
                (title, original_title, year, synopsis, episodes, duration, 
                is_deleted, created_at, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.executemany(anime_insert_query, anime_data)

                # Вставка аніме з тимчасової таблиці в основну
                cursor.execute("""
                INSERT INTO Anime 
                (title, original_title, year, synopsis, episodes, duration, 
                is_deleted, created_at, updated_at, updated_by)
                SELECT title, original_title, year, synopsis, episodes, duration, 
                is_deleted, created_at, updated_at, updated_by
                FROM #TempAnime
                """)

                # Видалення тимчасової таблиці
                cursor.execute("DROP TABLE #TempAnime")

                conn.commit()

    def generate_updates(self, entities, update_type='all', update_percentage=0.5):
        """
        Генерує оновлення для існуючих сутностей.

        Args:
            entities: результат виконання fetch_anime_simple або fetch_anime_with_relations
            update_type (str): тип оновлення ('all', 'anime', 'genres', 'reviews')
            update_percentage (float): відсоток сутностей, які потрібно оновити (0.0 - 1.0)

        Returns:
            dict: словник з оновленнями у форматі, готовому для використання в update_entities_batch методах
        """
        if not entities:
            return {}

        existing_genres = self.fetch_existing_genres()
        existing_users = self.fetch_existing_users()

        # Визначаємо кількість сутностей для оновлення
        num_to_update = max(1, int(len(entities) * update_percentage))
        entities_to_update = random.sample(list(entities), num_to_update)

        updates = {}

        for entity in entities_to_update:
            anime_id = entity[0]  # Припускаємо, що ID - перше поле
            update_data = {}

            # Генеруємо оновлення основних даних аніме
            if update_type in ['all', 'anime']:
                anime_updates = {}
                # Випадково вибираємо, які поля оновлювати
                if random.random() < 0.7:
                    anime_updates['title'] = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                if random.random() < 0.5:
                    anime_updates['original_title'] = ''.join(
                        random.choices(string.ascii_letters, k=random.randint(5, 20)))
                if random.random() < 0.3:
                    anime_updates['year'] = random.randint(1900, 2024)
                if random.random() < 0.4:
                    anime_updates['synopsis'] = '\n'.join([
                        ' '.join(random.choices(string.ascii_letters, k=random.randint(10, 50)))
                        for _ in range(random.randint(1, 5))
                    ])
                if random.random() < 0.3:
                    anime_updates['episodes'] = random.randint(1, 100)
                if random.random() < 0.3:
                    anime_updates['duration'] = random.randint(10, 120)
                if random.random() < 0.2:
                    anime_updates['is_deleted'] = random.choice([True, False])

                anime_updates['updated_at'] = datetime.datetime.now()
                anime_updates['updated_by'] = random.choice(existing_users)

                if anime_updates:
                    update_data['anime'] = anime_updates

            # Генеруємо оновлення жанрів
            if update_type in ['all', 'genres']:
                update_data['genres'] = random.sample(
                    [g[0] for g in existing_genres],
                    k=random.randint(1, min(5, len(existing_genres)))
                )

            # Генеруємо оновлення відгуків
            if update_type in ['all', 'reviews']:
                reviews = []
                for _ in range(random.randint(0, 10)):  # Може бути 0 відгуків
                    review = {
                        'user_id': random.choice(existing_users),
                        'rating': random.randint(1, 10),
                        'content': ' '.join(random.choices(string.ascii_letters, k=random.randint(20, 100))),
                        'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365)),
                        'updated_at': datetime.datetime.now()
                    }
                    reviews.append(review)
                update_data['reviews'] = reviews

            if update_data:
                updates[anime_id] = update_data

        return updates

    @measure_execution_time
    def get_top_rated_anime(self, n=10):
        """
        Отримує топ N аніме за середнім рейтингом.

        Args:
            n (int): кількість аніме для виведення

        Returns:
            list: список кортежів (id, title, avg_rating)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM GetTopRatedAnime(?)", (n,))
                return cursor.fetchall()
            except pyodbc.Error as e:
                print(f"Помилка при отриманні топ аніме: {str(e)}")
                return []

    @measure_execution_time
    def get_average_anime_rating(self, anime_id):
        """
        Отримує середній рейтинг для конкретного аніме.

        Args:
            anime_id (int): ID аніме

        Returns:
            float: середній рейтинг або None, якщо рейтингів немає
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dbo.GetAverageAnimeRating(?)", (anime_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    @measure_execution_time
    def get_anime_by_genre(self, genre_name):
        """
        Отримує список аніме за назвою жанру.

        Args:
            genre_name (str): назва жанру для пошуку

        Returns:
            list: список кортежів (id, title, year)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM GetAnimeByGenre(?)", (genre_name,))
            return cursor.fetchall()