
import pytest
from app.utils.logging_config import get_logger, APP_NAME, setup_logging

def test_logger_initialization():
    logger = get_logger("test")
    assert logger.name == APP_NAME
    
def test_setup_logging():
    setup_logging()
    logger = get_logger()
    assert len(logger.handlers) > 0
    assert logger.level <= 20  # INFO level or lower
