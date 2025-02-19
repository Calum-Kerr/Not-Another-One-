import os
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.pdf_utils import PDFHandler
from app.ocr_processing import OCRProcessor
from app.config import Config

bp = Blueprint('main', __name__)

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
            
            # Check dependencies first
            if not OCRProcessor.check_dependencies():
                return jsonify({
                    'status': 'warning',
                    'message': 'Dependencies missing. Processing without OCR.',
                    'filename': filename,
                    'pages': PDFHandler.extract_text_with_attributes(filepath)
                })
            
            # Process with OCR
            ocr_path = OCRProcessor.process_pdf(filepath)
            pages_data = PDFHandler.extract_text_with_attributes(ocr_path)
            
            return jsonify({
                'status': 'success',
                'message': 'File processed successfully with OCR',
                'filename': filename,
                'pages': pages_data
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/edit', methods=['POST'])
def edit_pdf():
    data = request.json
    filename = data['filename']
    changes = data['changes']
    
    filepath = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
    
    # Apply changes and save
    doc = PDFHandler.update_text(filepath, changes)
    output_path = os.path.join(Config.UPLOAD_FOLDER, f"edited_{filename}")
    doc.save(output_path)
    
    return jsonify({'success': True, 'edited_file': f"edited_{filename}"})

@bp.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
    return send_file(filepath, as_attachment=True)
