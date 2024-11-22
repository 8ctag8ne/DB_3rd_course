from typing import Dict, List, Optional, Union
import random
import string
import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson.objectid import ObjectId

from performance_metrics import PerformanceMetrics, measure_execution_time


class MongoDatabase:
    def __init__(self, connection_string: str, database_name: str):
        """
        Ініціалізація підключення до MongoDB.

        Args:
            connection_string (str): Рядок підключення до MongoDB
            database_name (str): Назва бази даних
        """
        self.client = MongoClient(connection_string)
        self.db: Database = self.client[database_name]
        self.anime_collection: Collection = self.db.anime
        self.performance_metrics = PerformanceMetrics()

        # Створення індексів для оптимізації запитів
        # self.anime_collection.create_index([("title", 1)])
        # self.anime_collection.create_index([("year", 1)])
        # self.anime_collection.create_index([("genres.name", 1)])
        # self.anime_collection.create_index([("reviews.rating", 1)])

    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        return self.performance_metrics.get_statistics()

    # READ операції
    @measure_execution_time
    def fetch_anime_simple(self, filters=None, limit=10):
        """Простий варіант читання записів з колекції Anime."""
        query = {}
        if filters:
            query.update(filters)

        result = self.anime_collection.find(
            query,
            {'reviews': 0, 'genres': 0}  # Виключаємо вкладені документи для простого запиту
        ).limit(limit)

        return list(result)

    @measure_execution_time
    def fetch_anime_with_relations(self, filters=None, limit=10):
        """Читання записів з колекції Anime з вкладеними даними."""
        query = {}
        if filters:
            query.update(filters)

        result = self.anime_collection.find(query).limit(limit)
        return list(result)

    # CREATE операції
    @measure_execution_time
    def insert_anime_simple(self, anime_data: dict) -> str:
        """Простий варіант додавання запису в колекцію Anime."""
        # Додаємо службові поля
        if '_id' in anime_data:
            del anime_data['_id']

        anime_data['created_at'] = datetime.datetime.now()
        anime_data['updated_at'] = datetime.datetime.now()
        anime_data['genres'] = []  # Порожній масив для жанрів
        anime_data['reviews'] = []  # Порожній масив для відгуків

        result = self.anime_collection.insert_one(anime_data)
        return str(result.inserted_id)

    @measure_execution_time
    def insert_anime_with_relations(self, anime_data: dict, genres: List[dict], reviews: List[dict]) -> str:
        """Додавання запису в колекцію Anime з вкладеними даними."""
        # Підготовка документа для вставки
        document = {
            **anime_data,
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'genres': genres,
            'reviews': [{
                **review,
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            } for review in reviews]
        }

        result = self.anime_collection.insert_one(document)
        return str(result.inserted_id)

    # UPDATE операції
    @measure_execution_time
    def update_anime_simple(self, anime_id: str, updates: dict):
        """Простий варіант оновлення запису в колекції Anime."""
        updates['updated_at'] = datetime.datetime.now()

        self.anime_collection.update_one(
            {'_id': ObjectId(anime_id)},
            {'$set': updates}
        )

    @measure_execution_time
    def update_anime_with_relations(self, anime_id: str, anime_updates=None, genres=None, reviews=None):
        """Оновлення запису в колекції Anime з вкладеними даними."""
        update_operations = {}

        if anime_updates:
            anime_updates['updated_at'] = datetime.datetime.now()
            update_operations.update({f'$set.{k}': v for k, v in anime_updates.items()})

        if genres is not None:
            update_operations['$set'] = {'genres': genres}

        if reviews is not None:
            # Оновлюємо часові мітки для відгуків
            for review in reviews:
                review['updated_at'] = datetime.datetime.now()
            update_operations['$set'] = {'reviews': reviews}

        if update_operations:
            self.anime_collection.update_one(
                {'_id': ObjectId(anime_id)},
                update_operations
            )

    # DELETE операції
    @measure_execution_time
    def delete_anime_simple(self, anime_ids=None):
        """Видалення записів з колекції Anime."""
        if anime_ids:
            object_ids = [ObjectId(id_) for id_ in anime_ids]
            self.anime_collection.delete_many({'_id': {'$in': object_ids}})
        else:
            self.anime_collection.delete_many({})

    @measure_execution_time
    def delete_anime_with_relations(self, anime_ids=None):
        """
        В MongoDB немає потреби в окремому методі для видалення зв'язаних даних,
        оскільки вони зберігаються в тому ж документі. Тому цей метод ідентичний delete_anime_simple
        """
        self.delete_anime_simple(anime_ids)

    # Допоміжні методи
    def fetch_existing_genres(self) -> List[dict]:
        """Отримання унікальних жанрів з колекції."""
        return self.anime_collection.distinct('genres')

    def fetch_existing_users(self) -> List[str]:
        """Отримання унікальних користувачів з колекції."""
        return self.anime_collection.distinct('reviews.user_id')

    def generate_entities(self, num_entities: int) -> List[dict]:
        """Генерує колекцію сутностей аніме з вкладеними даними."""
        existing_users = self.fetch_existing_users() or ['default_user']

        entities = []
        for _ in range(num_entities):
            # Генерація жанрів
            genres = [
                {
                    'name': ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))),
                    'description': ''.join(random.choices(string.ascii_letters, k=random.randint(20, 50)))
                }
                for _ in range(random.randint(1, 5))
            ]

            # Генерація відгуків
            reviews = [
                {
                    'user_id': random.choice(existing_users),
                    'rating': random.randint(1, 10),
                    'content': ' '.join(random.choices(string.ascii_letters, k=random.randint(20, 100))),
                    'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365)),
                    'updated_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                }
                for _ in range(random.randint(1, 10))
            ]

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
                'updated_by': random.choice(existing_users),
                'genres': genres,
                'reviews': reviews
            }

            entities.append(anime)

        return entities

    @measure_execution_time
    def insert_entities_batch(self, entities: List[dict]):
        """Масове додавання колекції аніме."""
        if entities:
            # Видаляємо _id з кожної сутності, якщо він є
            for entity in entities:
                if '_id' in entity:
                    del entity['_id']

            self.anime_collection.insert_many(entities)

    @measure_execution_time
    def insert_entities_batch_simple(self, entities: List[dict]):
        """Масове додавання колекції аніме без вкладених даних."""
        simple_entities = []
        for entity in entities:
            simple_entity = entity.copy()
            # Видаляємо _id та вкладені дані
            simple_entity.pop('_id', None)
            simple_entity.pop('genres', None)
            simple_entity.pop('reviews', None)
            simple_entities.append(simple_entity)

        if simple_entities:
            self.anime_collection.insert_many(simple_entities)

    def generate_updates(self, entities: List[dict], update_type='all', update_percentage=0.5) -> Dict[str, dict]:
        """Генерує оновлення для існуючих сутностей."""
        if not entities:
            return {}

        # Визначаємо кількість сутностей для оновлення
        num_to_update = max(1, int(len(entities) * update_percentage))
        entities_to_update = random.sample(entities, num_to_update)
        existing_users = self.fetch_existing_users() or ['default_user']

        updates = {}

        for entity in entities_to_update:
            anime_id = str(entity['_id'])
            update_data = {}

            if update_type in ['all', 'anime']:
                anime_updates = {}
                if random.random() < 0.7:
                    anime_updates['title'] = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                if random.random() < 0.5:
                    anime_updates['original_title'] = ''.join(
                        random.choices(string.ascii_letters, k=random.randint(5, 20)))
                if random.random() < 0.3:
                    anime_updates['year'] = random.randint(1900, 2024)

                anime_updates['updated_at'] = datetime.datetime.now()
                anime_updates['updated_by'] = random.choice(existing_users)

                if anime_updates:
                    update_data['anime'] = anime_updates

            if update_type in ['all', 'genres']:
                update_data['genres'] = [
                    {
                        'name': ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))),
                        'description': ''.join(random.choices(string.ascii_letters, k=random.randint(20, 50)))
                    }
                    for _ in range(random.randint(1, 5))
                ]

            if update_type in ['all', 'reviews']:
                update_data['reviews'] = [
                    {
                        'user_id': random.choice(existing_users),
                        'rating': random.randint(1, 10),
                        'content': ' '.join(random.choices(string.ascii_letters, k=random.randint(20, 100))),
                        'created_at': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365)),
                        'updated_at': datetime.datetime.now()
                    }
                    for _ in range(random.randint(0, 10))
                ]

            if update_data:
                updates[anime_id] = update_data

        return updates

    @measure_execution_time
    def get_top_rated_anime(self, n=10) -> List[dict]:
        """Отримує топ N аніме за середнім рейтингом."""
        pipeline = [
            # Розгортаємо масив відгуків
            {'$unwind': '$reviews'},
            # Групуємо по аніме і рахуємо середній рейтинг
            {
                '$group': {
                    '_id': '$_id',
                    'title': {'$first': '$title'},
                    'avg_rating': {'$avg': '$reviews.rating'},
                    'total_reviews': {'$sum': 1}
                }
            },
            # Сортуємо за середнім рейтингом
            {'$sort': {'avg_rating': -1}},
            # Обмежуємо кількість результатів
            {'$limit': n}
        ]

        return list(self.anime_collection.aggregate(pipeline))

    @measure_execution_time
    def get_average_anime_rating(self, anime_id: str) -> Optional[float]:
        """Отримує середній рейтинг для конкретного аніме."""
        pipeline = [
            {'$match': {'_id': ObjectId(anime_id)}},
            {'$unwind': '$reviews'},
            {
                '$group': {
                    '_id': '$_id',
                    'avg_rating': {'$avg': '$reviews.rating'}
                }
            }
        ]

        result = list(self.anime_collection.aggregate(pipeline))
        return result[0]['avg_rating'] if result else None

    # @measure_execution_time
    # def get_anime_by_genre(self, genre_name: str) -> List[dict]:
    #     """Отримує список аніме за назвою жанру."""
    #     return list(self.anime_collection.find({'genres.name': genre_name}, {'_id': 1, 'title': 1, 'year': 1})