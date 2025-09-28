import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def measure_execution_time(func):
    """Decorator to measure the execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        logging.info(f"Function {func.__name__} executed in {execution_time:.2f} ms")
        return result
    return wrapper

@measure_execution_time
def example_task():
    """Simulate a task to measure performance."""
    time.sleep(0.1)  # Simulate a delay

if __name__ == "__main__":
    for _ in range(5):
        example_task()