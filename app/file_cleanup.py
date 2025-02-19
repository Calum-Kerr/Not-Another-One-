import os
import time
from datetime import datetime, timedelta
import threading
from app.config import Config

class FileCleanup:
    _cleanup_thread = None
    _active_sessions = {}  # Track active file sessions and their expiry times

    @classmethod
    def start_countdown_thread(cls, initial_time, filename):
        """Start or update countdown for a specific file"""
        now = datetime.now()
        expiry_time = now + timedelta(minutes=initial_time)
        cls._active_sessions[filename] = expiry_time

        def countdown():
            while True:
                now = datetime.now()
                # Get earliest expiry time
                if not cls._active_sessions:
                    break

                # Show time until next file expires
                earliest_expiry = min(cls._active_sessions.values())
                remaining = earliest_expiry - now
                
                if remaining.total_seconds() <= 0:
                    # Remove expired sessions
                    expired = [f for f, t in cls._active_sessions.items() if t <= now]
                    for f in expired:
                        del cls._active_sessions[f]
                        try:
                            filepath = os.path.join(Config.UPLOAD_FOLDER, f)
                            if os.path.exists(filepath):
                                os.remove(filepath)
                                print(f"\nRemoved expired file: {f}")
                        except Exception as e:
                            print(f"\nError removing file {f}: {str(e)}")
                
                if not cls._active_sessions:
                    break

                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                print(f"\rActive sessions: {len(cls._active_sessions)} - Next cleanup in: {minutes:02d}:{seconds:02d}", end='', flush=True)
                time.sleep(1)

        # Start new thread if not running
        if not cls._cleanup_thread or not cls._cleanup_thread.is_alive():
            cls._cleanup_thread = threading.Thread(target=countdown)
            cls._cleanup_thread.daemon = True
            cls._cleanup_thread.start()

    @classmethod
    def remove_session(cls, filename):
        """Remove a file session when done"""
        if filename in cls._active_sessions:
            del cls._active_sessions[filename]

    @classmethod
    def force_cleanup(cls):
        """Force cleanup while respecting active sessions"""
        now = datetime.now()
        upload_dir = Config.UPLOAD_FOLDER
        
        if not os.path.exists(upload_dir):
            return
            
        for filename in os.listdir(upload_dir):
            # Don't delete files that have active sessions
            if filename not in cls._active_sessions:
                try:
                    filepath = os.path.join(upload_dir, filename)
                    os.remove(filepath)
                    print(f"\nForce removed inactive file: {filename}")
                except Exception as e:
                    print(f"\nError removing file {filename}: {str(e)}")
