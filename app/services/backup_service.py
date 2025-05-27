import os
import shutil
import gzip
import tarfile
from datetime import datetime
import aiofiles
import asyncpg
import logging

class BackupService:
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

    async def create_backup(self, database_url: str):
        try:
            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_path}/backup_{timestamp}.sql.gz"
            
            # Connect to database
            conn = await asyncpg.connect(database_url)
            
            # Get schema
            schema = await conn.fetch("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            """)
            
            # Dump database
            async with aiofiles.open(backup_file, 'wb') as f:
                with gzip.GzipFile(fileobj=f, mode='wb') as gz:
                    for schema_record in schema:
                        schema_name = schema_record['schema_name']
                        
                        # Get all tables
                        tables = await conn.fetch(f"""
                            SELECT tablename 
                            FROM pg_tables 
                            WHERE schemaname = '{schema_name}'
                        """)
                        
                        for table in tables:
                            table_name = table['tablename']
                            
                            # Dump table schema
                            schema_dump = await conn.fetch(f"""
                                SELECT pg_get_tabledef('{schema_name}.{table_name}'::regclass)
                            """)
                            await gz.write(schema_dump[0][0].encode() + b'\n')
                            
                            # Dump table data
                            data = await conn.fetch(f"""
                                SELECT * FROM {schema_name}.{table_name}
                            """)
                            for record in data:
                                insert = f"INSERT INTO {schema_name}.{table_name} VALUES {record};\n"
                                await gz.write(insert.encode())
            
            # Create archive with media files
            media_backup = f"{self.backup_path}/media_{timestamp}.tar.gz"
            with tarfile.open(media_backup, "w:gz") as tar:
                tar.add("media", arcname="media")
            
            # Cleanup old backups (keep last 7 days)
            self._cleanup_old_backups()
            
            logging.info(f"Backup created successfully: {backup_file}")
            return True
            
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return False

    def _cleanup_old_backups(self, keep_days: int = 7):
        current_time = datetime.now()
        for filename in os.listdir(self.backup_path):
            file_path = os.path.join(self.backup_path, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            if (current_time - file_time).days > keep_days:
                os.remove(file_path)
                logging.info(f"Removed old backup: {filename}")

    async def restore_backup(self, backup_file: str):
        try:
            if not os.path.exists(backup_file):
                raise FileNotFoundError("Backup file not found")
                
            # Extract SQL
            if backup_file.endswith('.gz'):
                with gzip.open(backup_file, 'rt') as f:
                    sql_commands = f.read()
            else:
                with open(backup_file, 'r') as f:
                    sql_commands = f.read()
            
            # Execute SQL
            conn = await asyncpg.connect(self.database_url)
            await conn.execute(sql_commands)
            
            # Restore media files if exists
            media_backup = backup_file.replace('.sql.gz', '_media.tar.gz')
            if os.path.exists(media_backup):
                with tarfile.open(media_backup, "r:gz") as tar:
                    tar.extractall("media")
            
            logging.info(f"Backup restored successfully: {backup_file}")
            return True
            
        except Exception as e:
            logging.error(f"Restore failed: {e}")
            return False
