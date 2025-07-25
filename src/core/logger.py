"""
Logging configuration for LinkedIn Analyzer Agent
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> None:
    """Setup application logging"""
    
    # Use settings defaults if not provided
    level = log_level or settings.LOG_LEVEL
    file_path = log_file or settings.LOG_FILE
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {level}, File: {file_path}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class ContextLogger:
    """Context-aware logger for request tracking"""
    
    def __init__(self, logger: logging.Logger, context: dict = None):
        self.logger = logger
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context"""
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"[{context_str}] {message}"
        return message
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(self._format_message(message), **kwargs)
    
    def add_context(self, **kwargs):
        """Add context to the logger"""
        self.context.update(kwargs)
        return self
    
    def clear_context(self):
        """Clear all context"""
        self.context.clear()
        return self
