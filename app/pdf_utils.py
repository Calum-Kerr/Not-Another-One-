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
            text_page = page.get_text("dict")
            
            for block in text_page["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        # Combine spans in the same line
                        line_text = ""
                        first_span = line["spans"][0]
                        line_bbox = list(first_span['bbox'])
                        
                        # Collect all text and extend bbox if needed
                        for span in line["spans"]:
                            line_text += span['text']
                            line_bbox[2] = max(line_bbox[2], span['bbox'][2])
                            line_bbox[3] = max(line_bbox[3], span['bbox'][3])
                        
                        # Only add non-empty lines
                        if line_text.strip():
                            blocks.append({
                                'text': line_text,
                                'bbox': line_bbox,
                                'font': first_span['font'],
                                'size': first_span['size'],
                                'flags': first_span['flags'],
                                'color': first_span['color']
                            })
            
            pages_data.append(blocks)
        
        doc.close()  # Close the document to free resources
        return pages_data

    @staticmethod
    def normalize_color(color):
        """Convert color values to range 0-1"""
        if not color or not isinstance(color, (list, tuple)):
            return (0, 0, 0)
        return tuple(max(0, min(1, c/255)) if c > 1 else c for c in color[:3])

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
                
                # Calculate precise white rectangle dimensions with adjusted position
                text_height = change['size'] * 1
                y_middle = (y0 + y1) / 2
                rect_y0 = y_middle - (text_height / 2) + 1  # Move down 0.5 pixel
                rect_y1 = y_middle + (text_height / 2) + 1  # Move down 0.5 pixel
                
                # Adjust x position (move right 0.5 pixel)
                x_offset = -0.5  # Changed from -1 to -0.5 to move right
                rect_x0 = x0 + x_offset
                rect_x1 = rect_x0 + text_width
                
                # Create precise white rectangle
                page.draw_rect([rect_x0, rect_y0, rect_x1, rect_y1], 
                             color=(1, 1, 1), 
                             fill=(1, 1, 1))
                
                # Position text with same adjustments
                text_x = rect_x0
                text_y = y1 - (change['size'] * 0.1) + 0  # Adjust for new position
                
                try:
                    # Insert text with preserved color
                    color = PDFHandler.normalize_color(change.get('color', (0, 0, 0)))
                    
                    # Draw text
                    page.insert_text(
                        point=(text_x, text_y),
                        text=change['new_text'],
                        fontname=font,
                        fontsize=change['size'],
                        color=color
                    )
                    
                    # Draw underline for links if needed
                    if isinstance(change.get('color'), (list, tuple)) and len(change['color']) >= 3:
                        if change['color'][0] == 0 and change['color'][1] == 0 and change['color'][2] > 0:
                            underline_y = rect_y1 - 0.5
                            page.draw_line(
                                (rect_x0, underline_y),
                                (rect_x1, underline_y),
                                color=color,
                                width=0.5
                            )
                    
                except Exception as e:
                    print(f"Text insertion error: {str(e)}, using fallback method")
                    # Fallback handling...
                    
        return doc
