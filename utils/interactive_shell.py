# utils/interactive_shell.py
import time

def launch_interactive_shell(context):
    """
    Launches an interactive Python shell with preserved context
    :param context: Dictionary of objects to make available
    """
    print("\n--- ENTERING INTERACTIVE MODE ---")
    print("Browser session preserved. Type commands to execute.")
    print("Special commands: 'exit' to quit, 'screenshot' to capture")
    
    # Add helper functions to context
    context['help'] = lambda: print("Available objects:", ", ".join(context.keys()))
    context['screenshot'] = lambda: save_screenshot(context)
    
    while True:
        try:
            command = input("\n>>> ")
            
            if command.lower() == 'exit':
                break
                
            if command.lower() == 'screenshot':
                context['screenshot']()
                continue
                
            try:
                # Try as expression
                result = eval(command, globals(), context)
                if result is not None:
                    print(f"Result: {result}")
            except SyntaxError:
                # Execute as statement
                exec(command, globals(), context)
                
        except Exception as e:
            print(f"Execution error: {e}")

def save_screenshot(context):
    """Helper to save screenshot with timestamp"""
    if 'driver' in context:
        filename = f"screenshot_{int(time.time())}.png"
        context['driver'].save_screenshot(filename)
        print(f"Screenshot saved as {filename}")
    else:
        print("No driver available for screenshot")