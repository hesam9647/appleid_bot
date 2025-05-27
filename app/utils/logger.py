import logging
import logging.handlers
import os
from datetime import datetime

def setup_logger():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Setup logger
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.INFO)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        filename=f'logs/bot_{datetime.now().strftime("%Y-%m-%d")}.log',
        maxBytes=5242880,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=f'logs/errors_{datetime.now().strftime("%Y-%m-%d")}.log',
        maxBytes=5242880,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger
