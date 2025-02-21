import os
from datetime import timedelta

class Config:
    # Use Heroku's environment variables if available
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # Use temporary directory on Heroku
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'uploads')
    
    # Adjust file size limit based on your Heroku plan
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))
    
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

    @staticmethod
    def init_app(app):
        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Clear any existing files in upload directory
        for filename in os.listdir(Config.UPLOAD_FOLDER):
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Error: {e}')
