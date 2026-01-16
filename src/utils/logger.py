import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

logs_dir = Path(__file__).parent.parent.parent / 'logs'
logs_dir.mkdir(exist_ok=True)

logger = logging.getLogger('fresha_automation')
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler_error = RotatingFileHandler(
    logs_dir / 'error.log',
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)
file_handler_error.setLevel(logging.ERROR)
file_handler_error.setFormatter(formatter)

file_handler_all = RotatingFileHandler(
    logs_dir / 'combined.log',
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)
file_handler_all.setLevel(logging.INFO)
file_handler_all.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler_error)
logger.addHandler(file_handler_all)
logger.addHandler(console_handler)
