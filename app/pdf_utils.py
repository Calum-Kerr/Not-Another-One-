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
                x0, y0, x1, y1 = change['bbox']
                
                # Calculate font and style
                font = 'helv'
                if 'Times' in change['font']:
                    font = 'tiro'
                elif 'Courier' in change['font']:
                    font = 'cour'
                
                if 'Bold' in change['font'] or (change.get('flags', 0) & 2**1):
                    font = f"{font},bold"
                if 'Italic' in change['font'] or (change.get('flags', 0) & 2**0):
                    font = f"{font},italic"
                
                # Get exact text width
                text_width = PDFHandler.get_text_width(
                    change['new_text'],
                    font,
                    change['size']
                )
                
                # Calculate dimensions
                text_height = change['size'] * 1
                y_middle = (y0 + y1) / 2
                rect_y0 = y_middle - (text_height / 2) + 1
                rect_y1 = y_middle + (text_height / 2) + 1
                
                x_offset = -0.5
                rect_x0 = x0 + x_offset
                rect_x1 = rect_x0 + text_width
                
                # Draw white background
                page.draw_rect([rect_x0, rect_y0, rect_x1, rect_y1], 
                             color=(1, 1, 1), 
                             fill=(1, 1, 1))
                
                # Get original color from the span
                original_color = change.get('color', [0, 0, 0])
                if isinstance(original_color, (list, tuple)) and len(original_color) >= 3:
                    color = PDFHandler.normalize_color(original_color)
                else:
                    color = (0, 0, 0)  # Default to black
                
                # Draw text with original color
                text_x = rect_x0
                text_y = y1 - (change['size'] * 0.1) + 0
                
                page.insert_text(
                    point=(text_x, text_y),
                    text=change['new_text'],
                    fontname=font,
                    fontsize=change['size'],
                    color=color
                )
                
                # Handle links (blue text)
                r, g, b = original_color[:3]
                if r == 0 and g == 0 and b > 0:  # Blue text
                    underline_y = rect_y1 - 0.5
                    page.draw_line(
                        (rect_x0, underline_y),
                        (rect_x1, underline_y),
                        color=color,
                        width=0.5
                    )
        
        return doc
