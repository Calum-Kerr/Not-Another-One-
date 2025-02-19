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
    def normalize_color(color):
        """Convert color values to range 0-1"""
        if not color or not isinstance(color, (list, tuple)):
            return (0, 0, 0)
        return tuple(max(0, min(1, c/255)) if c > 1 else c for c in color[:3])

    @staticmethod
    def update_text(pdf_path, changes):
        """Apply text changes to PDF"""
        doc = fitz.open(pdf_path)
        
        for page_num, page_changes in changes.items():
            page = doc[int(page_num)]
            
            for change in page_changes:
                x0, y0, x1, y1 = change['bbox']
                
                # Calculate white rectangle dimensions with lower position
                text_height = change['size'] * 1
                y_middle = (y0 + y1) / 2
                rect_y0 = y_middle - (text_height / 2) + 0.5  # Move down 2 pixels
                rect_y1 = y_middle + (text_height / 2) + 0.5  # Move down 2 pixels
                
                # Adjust width based on text length difference
                original_len = len(change.get('original_text', ''))
                new_len = len(change['new_text'])
                char_width = (x1 - x0) / max(original_len, 10)  # Avoid division by zero
                new_width = char_width * new_len
                rect_x1 = x0 + new_width
                
                # Create adjusted white rectangle
                page.draw_rect([x0, rect_y0, rect_x1, rect_y1], 
                             color=(1, 1, 1), 
                             fill=(1, 1, 1))
                
                # Adjust text position
                text_x = x0 + 0.8
                text_y = y1 - (change['size'] * 0.1)
                
                try:
                    # Set up font
                    base_font = 'helv'
                    if 'Times' in change['font']:
                        base_font = 'tiro'
                    elif 'Courier' in change['font']:
                        base_font = 'cour'
                    
                    # Handle text styling
                    if 'Bold' in change['font'] or (change.get('flags', 0) & 2**1):
                        base_font = f"{base_font},bold"
                    if 'Italic' in change['font'] or 'Oblique' in change['font'] or (change.get('flags', 0) & 2**0):
                        base_font = f"{base_font},italic"
                    
                    # Preserve original color for links (blue usually)
                    color = change.get('color', (0, 0, 0))
                    if isinstance(color, (list, tuple)) and len(color) >= 3:
                        if color[0] == 0 and color[1] == 0 and color[2] > 0:  # If it's a blue link
                            # Draw underline with matching color
                            underline_y = rect_y1 - 0.5
                            page.draw_line(
                                (x0, underline_y),
                                (rect_x1, underline_y),
                                color=PDFHandler.normalize_color(color),
                                width=0.5
                            )
                    
                    # Insert text with preserved color
                    page.insert_text(
                        point=(text_x, text_y),
                        text=change['new_text'],
                        fontname=base_font,
                        fontsize=change['size'],
                        color=PDFHandler.normalize_color(color)
                    )
                    
                except Exception as e:
                    print(f"Text insertion error: {str(e)}, using fallback method")
                    page.insert_text(
                        point=(text_x, text_y),
                        text=change['new_text'],
                        fontname='helv',
                        fontsize=change['size'],
                        color=(0, 0, 0)
                    )
        
        return doc
