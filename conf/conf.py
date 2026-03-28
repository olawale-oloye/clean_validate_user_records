"""Logger configuration for the main package."""
from pathlib import Path
import logging
from typing import Sequence
# Base Directory = folder containing this file (conf.py)
BASE_DIR = Path(__file__).resolve().parent
# Project root
PROJECT_ROOT= BASE_DIR.parent
# Log Directory
LOG_DIR = PROJECT_ROOT/"logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
# Log file path
log_path = LOG_DIR /"logs.log"
# Logging Configuration
handlers: Sequence[logging.Handler] = [
    logging.FileHandler(log_path, encoding="utf-8"),
    logging.StreamHandler()
]
logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s - %(levelname)s  - %(message)s ",
    datefmt="%Y-%m-%d  %H:%M",
    handlers=handlers,
    force=True
)
logger = logging.getLogger(__name__)