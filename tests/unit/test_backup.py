
import pytest
import os
from datetime import datetime
from pathlib import Path
from scripts.backup_db import backup_database

@pytest.fixture
def setup_test_db(tmp_path):
    """Create a test database file"""
    test_db = tmp_path / "test.db"
    test_db.write_text("test data")
    return test_db

def test_backup_creation(tmp_path, setup_test_db):
    backup_dir = tmp_path / "backups"
    source_db = setup_test_db
    
    # Run backup
    backup_database()
    
    # Verify backup was created
    assert backup_dir.exists()
    backup_files = list(backup_dir.glob("gold_investment_*.db"))
    assert len(backup_files) > 0

def test_backup_rotation(tmp_path, setup_test_db):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Create 6 test backups
    for i in range(6):
        backup_file = backup_dir / f"gold_investment_test_{i}.db"
        backup_file.write_text("test")
    
    # Run backup
    backup_database()
    
    # Verify only 5 backups remain
    backup_files = list(backup_dir.glob("gold_investment_*.db"))
    assert len(backup_files) == 5

def test_backup_naming(tmp_path, setup_test_db):
    backup_database()
    backup_dir = Path("instance/backups")
    backup_files = list(backup_dir.glob("gold_investment_*.db"))
    
    assert len(backup_files) > 0
    backup_name = backup_files[0].name
    
    # Verify backup name format
    assert backup_name.startswith("gold_investment_")
    assert backup_name.endswith(".db")
    
    # Verify timestamp format in filename
    timestamp = backup_name.replace("gold_investment_", "").replace(".db", "")
    assert len(timestamp) == 15  # YYYYMMdd_HHMMSS format
