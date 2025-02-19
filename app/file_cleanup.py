import os
import time
from datetime import datetime, timedelta
import threading
from app.config import Config

class FileCleanup:
    _cleanup_thread = None

    @classmethod
    def start_countdown_thread(cls, initial_time):
        """Start a thread to show countdown in terminal"""
        def countdown():
            end_time = datetime.now() + timedelta(minutes=initial_time)
            
            while datetime.now() < end_time:
                remaining = end_time - datetime.now()
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                print(f"\rTime until cleanup: {minutes:02d}:{seconds:02d}", end='', flush=True)
                time.sleep(5)  # Update every 5 seconds
                
            print("\nCleaning up files...")
            cls.force_cleanup()

        if cls._cleanup_thread and cls._cleanup_thread.is_alive():
            return  # Don't start new thread if one is running
            
        cls._cleanup_thread = threading.Thread(target=countdown)
        cls._cleanup_thread.daemon = True
        cls._cleanup_thread.start()

    @staticmethod
    def cleanup_old_files():
        """Remove files that have exceeded retention period"""
        now = datetime.now()
        upload_dir = Config.UPLOAD_FOLDER
        
        if not os.path.exists(upload_dir):
            return
            
        for filename in os.listdir(upload_dir):
            filepath = os.path.join(upload_dir, filename)
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                age = now - file_time
                
                if age > Config.FILE_RETENTION_PERIOD:
                    os.remove(filepath)
                    print(f"\nRemoved file: {filename}")
            except Exception as e:
                print(f"\nError processing file {filename}: {str(e)}")

    @staticmethod
    def force_cleanup():
        """Force remove all files"""
        upload_dir = Config.UPLOAD_FOLDER
        
        if not os.path.exists(upload_dir):
            return
            
        for filename in os.listdir(upload_dir):
            try:
                filepath = os.path.join(upload_dir, filename)
                os.remove(filepath)
                print(f"\nForce removed: {filename}")
            except Exception as e:
                print(f"\nError removing file {filename}: {str(e)}")
