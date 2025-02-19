import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Standard PDF fonts available
    STANDARD_FONTS = {
        'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique',
        'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
        'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',
        'Symbol', 'ZapfDingbats'
    }
    
    # Default fallback font
    DEFAULT_FONT = 'Times-Roman'
    
    # File cleanup settings
    FILE_RETENTION_PERIOD = timedelta(minutes=2)  # Initial 2 minute retention
    FINAL_CLEANUP_DELAY = timedelta(minutes=2)  # Additional 2 minutes before complete cleanup
    CLEANUP_INTERVAL = timedelta(minutes=1)  # Check every minute
    LAST_CLEANUP_TIME = None
