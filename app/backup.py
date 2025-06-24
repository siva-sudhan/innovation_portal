import os
import shutil
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Paths
# Use the same location as SQLALCHEMY_DATABASE_URI which points to
# a SQLite file relative to the application package directory.
# This ensures the backup job looks for the correct database file.
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'innovation.db')
BACKUP_DIR = os.path.join(os.path.abspath(os.path.join(BASE_DIR, '..')), 'db_backups')

scheduler = BackgroundScheduler()


def backup_database():
    """Copy the database file to a timestamped backup."""
    if not os.path.exists(DB_PATH):
        print('[Backup] Database file not found; skipping backup.')
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'innovation_{timestamp}.db')
    shutil.copy2(DB_PATH, backup_file)
    print(f'[Backup] Database backed up to {backup_file}')


def restore_latest_backup():
    """Restore the most recent backup if the main database is missing."""
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        return

    if not os.path.exists(BACKUP_DIR):
        print('[Backup] No backup directory found; nothing to restore.')
        return

    backups = sorted(
        (f for f in os.listdir(BACKUP_DIR) if f.endswith('.db'))
    )
    if not backups:
        print('[Backup] No backup files found to restore.')
        return

    latest = os.path.join(BACKUP_DIR, backups[-1])
    shutil.copy2(latest, DB_PATH)
    print(f'[Backup] Restored database from {latest}')


def start_scheduler():
    """Start the hourly backup scheduler."""
    if scheduler.running:
        return

    scheduler.add_job(
        backup_database,
        'interval',
        hours=1,
        next_run_time=datetime.utcnow(),
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
