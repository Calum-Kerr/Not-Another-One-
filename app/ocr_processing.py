import ocrmypdf
import tempfile
from pathlib import Path
import shutil
import subprocess
import os

class OCRProcessor:
    @staticmethod
    def check_dependencies():
        """Check if required dependencies are available"""
        try:
            # Check Ghostscript
            subprocess.run(['gs', '--version'], check=True, capture_output=True)
            # Check Tesseract
            subprocess.run(['tesseract', '--version'], check=True, capture_output=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def process_pdf(input_path):
        """Process PDF with OCR if possible, otherwise return original file"""
        if not OCRProcessor.check_dependencies():
            print("Warning: Missing dependencies. Please run setup_dependencies.sh")
            return input_path

        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                output_path = tmp_file.name
                
            ocrmypdf.ocr(
                input_path,
                output_path,
                force_ocr=True,
                skip_text=False,
                optimize=0,
                output_type='pdf',
                use_threads=True,
                language='eng',
                progress_bar=False
            )
            return output_path
        except Exception as e:
            print(f"OCR processing failed: {str(e)}")
            return input_path
