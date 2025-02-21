import fitz
from app.font_utils import get_fallback_font, preserve_text_attributes
from .text_color_handler import ColorHandler
from .link_handler import LinkHandler

class PDFHandler:
    # Built-in font mappings
    FONTS = {
        'normal': 'Helvetica',
        'bold': 'Helvetica-Bold',
        'italic': 'Helvetica-Oblique',
        'bold-italic': 'Helvetica-BoldOblique',
        'times': 'Times-Roman',
        'times-bold': 'Times-Bold',
        'times-italic': 'Times-Italic',
        'courier': 'Courier',
        'courier-bold': 'Courier-Bold',
        'courier-italic': 'Courier-Oblique'
    }

    @staticmethod
    def get_font_name(font_attributes):
        """Get built-in font name based on attributes"""
        is_bold = 'Bold' in font_attributes
        is_italic = 'Italic' in font_attributes or 'Oblique' in font_attributes
        is_times = 'Times' in font_attributes
        is_courier = 'Courier' in font_attributes

        if is_times:
            if is_bold and is_italic:
                return 'Times-BoldItalic'
            elif is_bold:
                return 'Times-Bold'
            elif is_italic:
                return 'Times-Italic'
            return 'Times-Roman'
        elif is_courier:
            if is_bold:
                return 'Courier-Bold'
            elif is_italic:
                return 'Courier-Oblique'
            return 'Courier'
        else:  # Default to Helvetica
            if is_bold and is_italic:
                return 'Helvetica-BoldOblique'
            elif is_bold:
                return 'Helvetica-Bold'
            elif is_italic:
                return 'Helvetica-Oblique'
            return 'Helvetica'

    @staticmethod
    def extract_text_with_attributes(pdf_path):
        """Extract text and its attributes from PDF"""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page in doc:
            blocks = []
            text_page = page.get_text("dict")  # Use dict instead of rawdict
            
            for block in text_page["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if 'text' not in span:
                                continue
                                
                            # Ensure proper color format
                            color = span.get('color', 0)
                            if isinstance(color, int):
                                color = [0, 0, 0]
                            elif isinstance(color, (list, tuple)):
                                color = list(color[:3])
                            else:
                                color = [0, 0, 0]

                            blocks.append({
                                'text': span['text'].strip(),
                                'bbox': span['bbox'],
                                'font': span.get('font', 'helv'),
                                'size': span.get('size', 12),
                                'flags': span.get('flags', 0),
                                'color': color
                            })
            
            # Only add pages with content
            if blocks:
                pages_data.append(blocks)
        
        doc.close()
        return pages_data

    @staticmethod
    def normalize_color(color):
        """Convert color values to range 0-1"""
        try:
            if isinstance(color, (list, tuple)) and len(color) >= 3:
                # Convert integer RGB (0-255) to float (0-1)
                return tuple(float(c) / 255 if c > 1 else float(c) for c in color[:3])
            return (0, 0, 0)  # Default black
        except:
            return (0, 0, 0)  # Fallback to black on error

    @staticmethod
    def get_text_width(text, font_name, font_size):
        """Calculate exact width of text in points"""
        try:
            # Create a temp doc to measure text
            doc = fitz.Document()
            page = doc.new_page()
            # Get text width using built-in function
            tw = page.get_text_width(text, fontname=font_name, fontsize=font_size)
            doc.close()
            return tw
        except:
            # Fallback: estimate based on average character width
            return len(text) * (font_size * 0.5)  # Approximate width

    @staticmethod
    def update_text(pdf_path, changes):
        """Apply text changes to PDF"""
        doc = fitz.open(pdf_path)
        
        for page_num, page_changes in changes.items():
            page = doc[int(page_num)]
            
            for change in page_changes:
                if LinkHandler.is_link_text(change['new_text']):
                    LinkHandler.apply_link_to_text(
                        doc, int(page_num), change['new_text'], 
                        change['bbox'], change.get('color')
                    )
                else:
                    x0, y0, x1, y1 = change['bbox']
                    
                    # Get proper built-in font
                    font_name = PDFHandler.get_font_name(change.get('font', 'Helvetica'))
                    
                    # White out original text
                    page.draw_rect([x0, y0, x1, y1], 
                                 color=(1, 1, 1), 
                                 fill=(1, 1, 1))
                    
                    # Adjust position - move bold text down by 1
                    x_offset = 1 if 'Bold' in font_name else 0
                    y_offset = 3 if 'Bold' in font_name else 3  # Same y-offset for both now
                    
                    # Insert new text with proper font and adjusted position
                    color = PDFHandler.normalize_color(change.get('color', [0, 0, 0]))
                    page.insert_text(
                        point=(x0 + x_offset, y1 - y_offset),
                        text=change['new_text'],
                        fontname=font_name,
                        fontsize=change['size'],
                        color=color
                    )
        
        return doc
