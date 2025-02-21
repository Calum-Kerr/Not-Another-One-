import os
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.pdf_utils import PDFHandler
from app.ocr_processing import OCRProcessor
from app.config import Config
from app.file_cleanup import FileCleanup
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

# Add this function to handle file cleanup
def cleanup_old_files():
    now = datetime.now()
    retention_period = Config.FILE_RETENTION_PERIOD.total_seconds()
    
    for filename in os.listdir(Config.UPLOAD_FOLDER):
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file_modified = os.path.getmtime(file_path)
        if (now - datetime.fromtimestamp(file_modified)).total_seconds() > retention_period:
            try:
                os.remove(file_path)
            except OSError:
                pass

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and file.filename.endswith('.pdf'):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Start countdown thread
            FileCleanup.start_countdown_thread(2, filename)
            
            # Process PDF without OCR first
            pages_data = PDFHandler.extract_text_with_attributes(filepath)
            
            # Only use OCR if no text was extracted
            if not any(pages_data):
                ocr_path = OCRProcessor.process_pdf(filepath)
                pages_data = PDFHandler.extract_text_with_attributes(ocr_path)
            
            # Format pages
            formatted_pages = {
                str(i): page for i, page in enumerate(pages_data) if page
            }
            
            if not formatted_pages:
                return jsonify({
                    'status': 'error',
                    'error': 'No text extracted from PDF'
                }), 400
                
            return jsonify({
                'status': 'success',
                'filename': filename,
                'pages': formatted_pages
            })
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/edit', methods=['POST'])
def edit_pdf():
    cleanup_old_files()  # Call cleanup before processing edit
    
    # Check if file is too old
    data = request.json
    filename = data['filename']
    filepath = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
    
    if os.path.exists(filepath):
        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if datetime.now() - modified_time > Config.FILE_RETENTION_PERIOD:
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': 'File has expired'}), 410
    
    changes = data['changes']
    
    # Apply changes and save
    doc = PDFHandler.update_text(filepath, changes)
    output_path = os.path.join(Config.UPLOAD_FOLDER, f"edited_{filename}")
    doc.save(output_path)
    
    return jsonify({'success': True, 'edited_file': f"edited_{filename}"})

@bp.route('/download/<filename>')
def download_file(filename):
    """Basic file download"""
    try:
        filepath = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath)
        return "File not found", 404
    except Exception as e:
        print(f"Download error: {e}")
        return str(e), 500

@bp.route('/cleanup', methods=['POST'])
def trigger_cleanup():
    """Endpoint to trigger forced cleanup"""
    try:
        FileCleanup.force_cleanup()
        return jsonify({'success': True, 'message': 'All files cleaned up'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
