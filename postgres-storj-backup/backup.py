#!/usr/bin/env python3
import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import logging
import time
import signal

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variable to control the main loop
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running
    logger.info("Received shutdown signal")
    running = False

def create_backup():
    """Creates a PostgreSQL database dump"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/tmp/backup_{timestamp}.sql.gz"
        
        # Database connection parameters
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_name = os.getenv('POSTGRES_DB')
        db_user = os.getenv('POSTGRES_USER')
        db_password = os.getenv('POSTGRES_PASSWORD')
        
        # Creating the dump
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-Z', '9'  # maximum compression
        ]
        
        with open(backup_file, 'wb') as f:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
            subprocess.run(['gzip', '-c'], stdin=process.stdout, stdout=f)
        
        logger.info(f"Backup created: {backup_file}")
        return backup_file
        
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return None

def upload_to_storj(file_path):
    """Uploads a file to Storj"""
    try:
        # Storj configuration (S3-compatible)
        access_key = os.getenv('STORJ_ACCESS_KEY')
        secret_key = os.getenv('STORJ_SECRET_KEY')
        endpoint = os.getenv('STORJ_ENDPOINT', 'https://gateway.storjshare.io')
        bucket_name = os.getenv('STORJ_BUCKET')
        
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # File upload
        s3_client.upload_file(
            file_path,
            bucket_name,
            os.path.basename(file_path)
        )
        
        logger.info(f"File uploaded to Storj: {os.path.basename(file_path)}")
        return True
        
    except NoCredentialsError:
        logger.error("Storj credentials not available")
        return False
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return False

def perform_backup():
    """Perform a single backup operation"""
    backup_file = create_backup()
    if backup_file:
        if upload_to_storj(backup_file):
            logger.info("Backup completed successfully")
            # Delete the local file after successful upload
            os.remove(backup_file)
            return True
        else:
            logger.error("Backup upload failed")
            return False
    else:
        logger.error("Backup creation failed")
        return False

def main():
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get backup interval from environment variable (default: 86400 seconds = 24 hours)
    backup_interval = int(os.getenv('BACKUP_INTERVAL_SECONDS', '86400'))
    logger.info(f"Starting backup service with interval: {backup_interval} seconds")
    
    # Perform initial backup immediately
    perform_backup()
    
    # Main loop
    while running:
        try:
            # Sleep for the specified interval
            time.sleep(backup_interval)
            
            # Perform backup
            if running:  # Check again after sleep in case we received a signal
                perform_backup()
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            # Continue running even if one backup fails
    
    logger.info("Backup service stopped")

if __name__ == "__main__":
    main()
