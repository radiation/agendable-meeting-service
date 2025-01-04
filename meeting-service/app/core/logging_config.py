import os
import sys

from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Get log level from environment or default to INFO
log_level = os.getenv("LOG_LEVEL", "INFO")

# Configure Loguru
logger.remove()
logger.add(
    "logs/app.log",
    level=log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    retention="1 month",
    compression="zip",
)
logger.add(sys.stdout, level=log_level)
