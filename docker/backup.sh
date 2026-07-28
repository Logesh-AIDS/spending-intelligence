#!/bin/bash
# Automated database backup script
# Run daily via cron: 0 2 * * * /opt/spending-intelligence/docker/backup.sh

set -euo pipefail

BACKUP_DIR="/backups/spending-intelligence"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..."

# PostgreSQL backup
if [ -n "${POSTGRES_HOST:-}" ]; then
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -F c \
        -f "$BACKUP_DIR/db_$DATE.dump"
    echo "[$(date)] PostgreSQL backup: db_$DATE.dump"
fi

# SQLite backup (development/single-server)
if [ -f "/app/spending.db" ]; then
    cp /app/spending.db "$BACKUP_DIR/sqlite_$DATE.db"
    echo "[$(date)] SQLite backup: sqlite_$DATE.db"
fi

# ML models backup
if [ -d "/app/ml/models" ]; then
    tar -czf "$BACKUP_DIR/models_$DATE.tar.gz" -C /app/ml models/
    echo "[$(date)] ML models backup: models_$DATE.tar.gz"
fi

# Remove backups older than retention period
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup complete. Retained last $RETENTION_DAYS days."
