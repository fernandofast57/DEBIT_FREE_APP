
import os
import shutil
from datetime import datetime
import sqlite3
from pathlib import Path

def backup_database():
    """Create a backup of the SQLite database"""
    source_db = "instance/gold_investment.db"
    backup_dir = "instance/backups"
    
    # Create backup directory if it doesn't exist
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/gold_investment_{timestamp}.db"
    
    # Create backup
    if os.path.exists(source_db):
        shutil.copy2(source_db, backup_file)
        print(f"Database backup created: {backup_file}")
    else:
        print("Source database not found")

if __name__ == "__main__":
    backup_database()
