import threading
import queue
import time

def execute_with_timeout(func, timeout: int, *args, **kwargs):
    """
    Execute a function with a timeout limit
    
    Args:
        func: Function to execute
        timeout: Maximum wait time in seconds
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Tuple (result, timed_out):
        - result: Return value of the function if completed in time
        - timed_out: Boolean indicating if timeout occurred
    """
    result_queue = queue.Queue()
    
    def worker():
        try:
            result = func(*args, **kwargs)
            result_queue.put((result, False))
        except Exception as e:
            result_queue.put((e, True))
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        return None, True  # Timeout occurred
    
    return result_queue.get() if not result_queue.empty() else (None, True)