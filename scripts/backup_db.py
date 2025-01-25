
import os
import shutil
from datetime import datetime
import sqlite3
from pathlib import Path
import logging
import schedule
import time

logger = logging.getLogger(__name__)

def backup_database():
    """Create a backup of the SQLite database"""
    source_db = "instance/gold_investment.db"
    backup_dir = "instance/backups"
    
    try:
        # Create backup directory if it doesn't exist
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/gold_investment_{timestamp}.db"
        
        # Create backup
        if os.path.exists(source_db):
            shutil.copy2(source_db, backup_file)
            logger.info(f"Database backup created: {backup_file}")
            
            # Keep only last 5 backups
            backups = sorted(Path(backup_dir).glob("gold_investment_*.db"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
                    logger.info(f"Removed old backup: {old_backup}")
        else:
            logger.error("Source database not found")
            
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")

def run_scheduled_backup():
    """Run scheduled backups"""
    schedule.every().day.at("00:00").do(backup_database)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(
        filename='logs/backup.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    run_scheduled_backup()
