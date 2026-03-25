# logging_config.py
import logging
from logging import FileHandler
import os
from logging.handlers import RotatingFileHandler

def ensure_directory_exists(filepath):
    """Create directory if doesn't exist"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def setup_logger(name, log_files, level=logging.INFO, formatter=None, 
                 max_bytes=10*1024*1024 , backup_count=5): # 10MB
    
    """Create logger that writes to multiple files"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not formatter:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    for log_file in log_files:
        ensure_directory_exists(log_file)
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Configure loggers (will auto-create folders)
llm_automation_logger = setup_logger(
    "llm_automation_logger",
    ["logs/llm_automation_process.log"],  # "logger" folder will be created
    level=logging.DEBUG,
    formatter=logging.Formatter('%(asctime)s - %(levelname)s \n%(message)s\n')
)

llm_app_conv_logger = setup_logger(
    "app.llm.conversation",
    ["logs/llm_app_conversation.log"],  # "logs" folder will be created
    formatter=logging.Formatter('%(asctime)s - %(levelname)s \n%(message)s\n')
)

dual_logger = setup_logger(
    "dual_logger",
    log_files=[
        "logs/llm_automation_process.log",
        "logs/llm_app_conversation.log"
    ],
    formatter=logging.Formatter('%(asctime)s - %(levelname)s \n%(message)s\n')
)