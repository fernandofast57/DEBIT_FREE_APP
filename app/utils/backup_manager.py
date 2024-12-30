import os
import shutil
from datetime import datetime
import hashlib
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
        
    def _ensure_backup_dir(self):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def _calculate_checksum(self, file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def create_backup(self, source_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup
            shutil.copy2(source_path, backup_path)
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Save metadata
            backup_info = {
                "timestamp": timestamp,
                "source": source_path,
                "checksum": checksum,
                "metadata": metadata or {}
            }
            
            meta_path = f"{backup_path}.meta"
            with open(meta_path, "w") as f:
                json.dump(backup_info, f, indent=2)
                
            logger.info(f"Backup created successfully: {backup_name}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise

    def verify_backup(self, backup_name: str) -> bool:
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            meta_path = f"{backup_path}.meta"
            
            if not os.path.exists(backup_path) or not os.path.exists(meta_path):
                return False
                
            with open(meta_path, "r") as f:
                backup_info = json.load(f)
                
            current_checksum = self._calculate_checksum(backup_path)
            return current_checksum == backup_info["checksum"]
            
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False

backup_manager = BackupManager()