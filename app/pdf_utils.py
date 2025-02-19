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
                # Get the coordinates from bbox
                x0, y0, x1, y1 = change['bbox']
                
                # Create white rectangle to cover old text
                page.draw_rect([x0, y0, x1, y1], color=(1, 1, 1), fill=(1, 1, 1))
                
                # Calculate text position (use bottom-left corner for text insertion)
                font = get_fallback_font(change['font'])
                fontsize = change['size']
                
                # Insert text at exact position
                page.insert_text(
                    point=(x0, y1),  # bottom-left corner
                    text=change['new_text'],
                    fontname=font,
                    fontsize=fontsize,
                    color=change.get('color', (0, 0, 0)),
                )
        
        return doc
