import functools
import time
from typing import Callable, Dict, Any
import statistics


class PerformanceMetrics:
    def __init__(self):
        self.metrics: Dict[str, list] = {}

    def add_execution_time(self, operation: str, execution_time: float):
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(execution_time)

    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        stats = {}
        for operation, times in self.metrics.items():
            if times:
                stats[operation] = {
                    'min': min(times),
                    'max': max(times),
                    'avg': statistics.mean(times),
                    'median': statistics.median(times),
                    'count': len(times)
                }
        return stats

    def clear(self):
        self.metrics = {}


def measure_execution_time(func: Callable):
    """Декоратор для вимірювання часу виконання методів класу MSSQLDatabase"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.perf_counter() - start_time
            self.performance_metrics.add_execution_time(func.__name__, execution_time)
            return result
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            self.performance_metrics.add_execution_time(f"{func.__name__}_error", execution_time)
            raise e

    return wrapper