import shutil
from pathlib import Path
from datetime import datetime
from src.utils.config import config
from src.utils.logger import logger

def backup_database(backup_dir: Path = None) -> Path:
    """Create a backup of the database"""
    if backup_dir is None:
        backup_dir = config.DB_PATH.parent / 'backups'
    
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'fresha_{timestamp}.db'
    
    try:
        if config.DB_PATH.exists():
            shutil.copy2(config.DB_PATH, backup_path)
            logger.info(f'Database backed up to {backup_path}')
            
            # Keep only last 10 backups
            backups = sorted(backup_dir.glob('fresha_*.db'), reverse=True)
            for old_backup in backups[10:]:
                old_backup.unlink()
                logger.info(f'Removed old backup: {old_backup}')
        else:
            logger.warn('Database file does not exist, skipping backup')
        
        return backup_path
    except Exception as e:
        logger.error(f'Backup failed: {e}')
        raise

def restore_database(backup_path: Path) -> bool:
    """Restore database from backup"""
    try:
        if not backup_path.exists():
            logger.error(f'Backup file not found: {backup_path}')
            return False
        
        # Create backup of current database before restore
        if config.DB_PATH.exists():
            current_backup = config.DB_PATH.parent / f'fresha_pre_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            shutil.copy2(config.DB_PATH, current_backup)
            logger.info(f'Current database backed up to {current_backup}')
        
        shutil.copy2(backup_path, config.DB_PATH)
        logger.info(f'Database restored from {backup_path}')
        return True
    except Exception as e:
        logger.error(f'Restore failed: {e}')
        return False
