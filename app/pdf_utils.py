import fitz
from app.font_utils import get_fallback_font, preserve_text_attributes

class PDFHandler:
    @staticmethod
    def extract_text_with_attributes(pdf_path):
        """Extract text and its attributes from PDF"""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page in doc:
            blocks = []
            for block in page.get_text("dict")["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            blocks.append({
                                'text': span['text'],
                                'bbox': span['bbox'],
                                'font': span['font'],
                                'size': span['size'],
                                'flags': span['flags'],
                                'color': span['color']
                            })
            pages_data.append(blocks)
        
        return pages_data

    @staticmethod
    def update_text(pdf_path, changes):
        """Apply text changes to PDF"""
        doc = fitz.open(pdf_path)
        
        for page_num, page_changes in changes.items():
            page = doc[int(page_num)]
            
            for change in page_changes:
                # Create redaction annotation
                page.add_redact_annot(change['bbox'])
                page.apply_redactions()
                
                # Insert new text
                font = get_fallback_font(change['font'])
                page.insert_textbox(
                    change['bbox'],
                    change['new_text'],
                    fontname=font,
                    fontsize=change['size'],
                    color=change.get('color', (0, 0, 0))
                )
        
        return doc
