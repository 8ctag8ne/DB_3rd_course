import json
import time
from typing import List, Dict, Any
import random
import statistics
from datetime import datetime


class DatabasePerformanceTester:
    def __init__(self, db, data_sizes: List[int], iterations: int = 3, output_file = f"db_performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"):
        """
        Ініціалізація тестера продуктивності.

        Args:
            db: екземпляр MSSQLDatabase
            data_sizes: список розмірів даних для тестування
            iterations: кількість повторень кожного тесту
        """
        self.db = db
        self.data_sizes = data_sizes
        self.iterations = iterations
        self.output_file = output_file
        self.results = {}

    def run_tests(self):
        """Запуск всіх тестів продуктивності."""
        try:
            for size in self.data_sizes:
                print(f"\nRunning tests for size: {size}")
                self.results[size] = {}

                for iteration in range(self.iterations):
                    print(f"Iteration {iteration + 1}/{self.iterations}")

                    # Генерація тестових даних
                    print("Generating test data...")
                    entities = self.db.generate_entities(size)

                    # Тестування операцій
                    self._test_batch_operations(size, entities)
                    self._test_single_operations(size)

                    # Очищення бази даних після кожної ітерації
                    print("Cleaning up database...")
                    self.db.delete_anime_with_relations()

                    # Невелика пауза між ітераціями
                    time.sleep(1)

            # Збереження результатів
                self._save_results(size)
                self.db.performance_metrics.clear()

        except Exception as e:
            print(f"Error during testing: {str(e)}")
            raise

    def _test_batch_operations(self, size: int, entities: List[Dict[str, Any]]):
        """Тестування операцій з багатьма записами."""
        operations = {
            'batch_insert_with_relations': lambda: self.db.insert_entities_batch(entities),
            'batch_insert_simple': lambda: self.db.insert_entities_batch_simple(entities),
            'batch_fetch_simple': lambda: self.db.fetch_anime_simple(limit=size),
            'batch_fetch_with_relations': lambda: self.db.fetch_anime_with_relations(limit=size)
        }

        for op_name, op_func in operations.items():
            try:
                print(f"Running {op_name}...")
                op_func()
            except Exception as e:
                print(f"Error in {op_name}: {str(e)}")

    def _test_single_operations(self, size: int):
        """Тестування операцій з одним записом у контексті заповненої бази даних."""
        single_entity = self.db.generate_entities(1)[0]
        if single_entity['anime']:
            simple_data = {
                'title': f"Test Single {datetime.now().isoformat()}",  # Унікальна назва
                'original_title': single_entity['anime']['original_title'],
                'year': single_entity['anime']['year'],
                'synopsis': single_entity['anime']['synopsis'],
                'episodes': single_entity['anime']['episodes'],
                'duration': single_entity['anime']['duration'],
                'is_deleted': single_entity['anime']['is_deleted'],
                'updated_by': single_entity['anime']['updated_by']
            }
        else:
            # Підготовка даних для операцій вставки
            simple_data = {
                'title': f"Test Single {datetime.now().isoformat()}",  # Унікальна назва
                'original_title': single_entity.get('original_title', "orig"),
                'year': single_entity['year'],
                'synopsis': single_entity['synopsis'],
                'episodes': single_entity['episodes'],
                'duration': single_entity['duration'],
                'is_deleted': single_entity['is_deleted']
            }
        relations_data = simple_data.copy()
        relations_data['title'] = simple_data['title'] + "_relations"

        operations = {
            'single_insert_simple': lambda: self.db.insert_anime_simple(simple_data),
            'single_insert_with_relations': lambda: self.db.insert_anime_with_relations(
                relations_data,
                single_entity['genres'],
                single_entity['reviews']
            ),
            'single_fetch_simple': lambda: self.db.fetch_anime_simple(limit=1),
            'single_fetch_with_relations': lambda: self.db.fetch_anime_with_relations(limit=1)
        }

        for op_name, op_func in operations.items():
            try:
                print(f"Running {op_name}...")
                op_func()
            except Exception as e:
                print(f"Error in {op_name}: {str(e)}")

    def _save_results(self, size):
        """Збереження результатів тестування у файл."""
        # Отримання статистики з performance_metrics
        stats = self.db.get_performance_stats()

        # Форматування результатів
        formatted_results = {
            'test_info': {
                'data_size': size,
                'iterations': self.iterations,
                'timestamp': datetime.now().isoformat()
            },
            'performance_stats': stats
        }

        # Збереження у JSON файл
        filename = self.output_file

        # Перевірка, чи файл вже існує та має вміст
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_content = f.read().strip()
        except FileNotFoundError:
            existing_content = ''

        # Відкриття файлу для запису
        with open(filename, 'w', encoding='utf-8') as f:
            # Якщо файл порожній, додаємо відкриваючу квадратну дужку
            if not existing_content:
                f.write('[\n')
            elif existing_content.endswith(']'):
                # Якщо файл вже містить масив, видаляємо закриваючу дужку
                f.seek(0)
                f.truncate()
                f.write(existing_content[:-1] + ',\n')
            else:
                # Якщо є вміст без дужок, додаємо кому та квадратні дужки
                f.seek(0)
                f.truncate()
                f.write('[\n' + existing_content + ',\n')

            # Додаємо поточний результат
            json.dump(formatted_results, f, indent=2, ensure_ascii=False)

            # Закриваємо масив
            f.write('\n]')

        print(f"\nResults saved to {filename}")

        # Виведення короткого звіту
        self._print_summary(stats)

    def _print_summary(self, stats: Dict[str, Dict[str, float]]):
        """Виведення короткого звіту про результати тестування."""
        print("\nPerformance Test Summary:")
        print("-" * 80)

        for operation, metrics in stats.items():
            print(f"\nOperation: {operation}")
            print(f"  Average time: {metrics['avg']:.4f} seconds")
            print(f"  Median time: {metrics['median']:.4f} seconds")
            print(f"  Min time: {metrics['min']:.4f} seconds")
            print(f"  Max time: {metrics['max']:.4f} seconds")
            print(f"  Number of executions: {metrics['count']}")