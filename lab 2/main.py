import json
from typing import Dict, Any

from mongo_database import MongoDatabase
from ms_sql_database import MSSQLDatabase
from database_tester import DatabasePerformanceTester


def format_performance_results(output_file: str) -> Dict[str, Any]:
    """
    Read and parse JSON performance test results from a file.

    Args:
        output_file (str): Path to the JSON file with performance test results

    Returns:
        Dict[str, Any]: Formatted and validated JSON object
    """
    try:
        # Read the entire file content
        with open(output_file, 'r', encoding='utf-8') as f:
            # If the file contains multiple JSON objects, parse them into a list
            raw_content = f.read().strip()

            # Handle potential multiple JSON objects in the file
            if raw_content.startswith('['):
                # If already a JSON array, load directly
                results = json.loads(raw_content)
            else:
                # If multiple JSON objects are written sequentially, split and parse
                json_strings = raw_content.split('\n}\n{')
                results = []
                for idx, json_str in enumerate(json_strings):
                    # Add back the braces that were stripped during splitting
                    if idx > 0:
                        json_str = '{' + json_str
                    if idx < len(json_strings) - 1:
                        json_str += '}'

                    results.append(json.loads(json_str))

        # Optional: Validate the structure
        for result in results:
            assert 'test_info' in result, "Missing test_info in result"
            assert 'performance_stats' in result, "Missing performance_stats in result"

        return results if len(results) > 1 else results[0]

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}
    except AssertionError as e:
        print(f"Validation error: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}

def test_database_with_logs(output_file, connection, db_name = None):
    if db_name is None:
        db = MSSQLDatabase(connection)
    else:
        db = MongoDatabase(connection, db_name)
    # Визначення розмірів даних для тестування
    data_sizes = [10, 100, 1000, 10000]
    # data_sizes = [10]
    iterations = 5  # Кількість повторень для кожного розміру
    tester = DatabasePerformanceTester(db, data_sizes, iterations, output_file)
    try:
        print("Starting performance tests...")
        tester.run_tests()
        print("\nTests completed successfully!")

    except Exception as e:
        print(f"\nError during testing: {str(e)}")

    finally:
        # Очищення бази даних після всіх тестів
        print("\nFinal cleanup...")
        db.delete_anime_with_relations()
        print("Cleanup completed")


mssql_connection_string = (
    r'DRIVER={SQL Server};'
    r'SERVER=DESKTOP-GP0Q10M\SQLEXPRESS01;'
    r'DATABASE=AnimeDB;'
    r'Trusted_Connection=yes;'
)
mongo_connection_string = r'mongodb://localhost:27017/'
mongo_name = 'AnimeDB'

test_database_with_logs("mongo_logs_new.json", mongo_connection_string, mongo_name)
test_database_with_logs("sql_logs_new.json", mssql_connection_string)

