from os import makedirs as os_makedirs
from traceback import format_exception
from datetime import datetime
from .env import get_env_var

LOG_PRINTING_ENABLED = get_env_var("LOG_PRINTING_ENABLED") == "true"
log_text = ""

# Not the best way, but I needed a way to toggle
def log(message: str):
    global log_text
    if LOG_PRINTING_ENABLED: print(message)
    log_text += f"{message}\n"

def log_exception(exception: Exception):
    global log_text
    bar = "=" * 100
    message = f"\n{bar}\n"
    message += "".join(format_exception(exception))
    message += f"{bar}\n"
    
    if LOG_PRINTING_ENABLED: print(message)
    log_text += f"{message}\n"
    
def export_log_text():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    destination_dir = "./logs"
    
    os_makedirs(destination_dir, exist_ok=True)
    with open(f"{destination_dir}/log_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(log_text)
