# error_handler.py
from datetime import datetime
import functools
import traceback

def handle_errors(log_error_callback=None, exception_type="Exception", message=""):
    """Universal decorator for all error handling"""
    exceptions = {
        "Exception": Exception
    }

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions[exception_type] as e:
                # Determine context based on arg type
                context_target = args[0]  # self reference
                
                now = datetime.now()
                # Build context info
                context = {
                    "action": func.__name__,
                    "class": type(context_target).__name__,
                    "args": args[1:],  # Skip self
                    "kwargs": kwargs,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Enhanced context for elements
                if hasattr(context_target, 'webelement'):
                    context.update({
                        "tag": context_target.get_tag_name(),
                        "text": context_target.get_text()[:50],
                    })
                
                print(f"\n⛔ ERROR in {context['class']}.{context['action']} at {context['timestamp']}")
                print(f"   Args: {context['args']}")
                print(f"   Error: {context['error']}")
                
                # Propagate error to callback if exists
                if log_error_callback:
                    log_error_callback(e, context)
                
                return
        return wrapper
    return decorator