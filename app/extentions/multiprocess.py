from concurrent.futures import ProcessPoolExecutor
import time
import traceback
from app.extentions.common_extensions import split_list
import math


class MultiProcess:
    def __init__(self, max_workers= 6):
        self.max_workers = max_workers
        
    
    def process(self, func, main_preference, other_preferences, user_preference):
        split_count = math.floor(len(other_preferences)/ self.max_workers)
        print("Split Count: ", split_count)
        dividedList = split_list(other_preferences, split_count)
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(func, main_preference, other_preference, user_preference)for other_preference in dividedList]
                results = [future.result() for future in futures]
            
            # converting list of dict into dict
            combined = {}
            for d in results:
                for k, v in d.items():
                    combined[k] = v
                    
            return combined
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            filename, line_number, func_name, text = tb[-1]
            traceback.print_exc()
            
            print(f"Error: {tb}")
            print(f"Error occurred: {e}")
            return None

# def worker(first, second, third):
#     print(f"Stating {first, second, third}")
#     time.sleep(5)  # Simulate a time-consuming task
#     print(f"Finished {first}")
#     return f"{first, second, third} completed"

# if __name__ == "__main__":

#     start_time = time.time()
#     tasks = ['task1', 'task2', 'task3', 'task4', 'task5']
#     multiProcess = MultiProcess()
#     results = multiProcess.process(worker, "HI User", tasks, "Endpoint")
#     print("Results:", results)
#     end_time = time.time()
#     print(f'Total time taken: {end_time - start_time:.2f} seconds')