from fitz import Document

class ColorHandler:
    @staticmethod
    def is_colored_text(color):
        """Check if text has non-black color"""
        if not color or not isinstance(color, (list, tuple)):
            return False
        # More precise color check
        return any(abs(c) > 0.01 for c in color[:3])  # Use small threshold

    @staticmethod
    def is_link_color(color):
        """Check if color matches typical link blue"""
        if not color or not isinstance(color, (list, tuple)):
            return False
        return color[0] == 0 and color[1] == 0 and color[2] > 0

    @staticmethod
    def preserve_color_on_edit(original_text, new_text, color):
        """Preserve original text color when editing"""
        if not ColorHandler.is_colored_text(color):
            return new_text
            
        # Normalize color values
        normalized_color = [c/255 if c > 1 else c for c in color[:3]]
        return f'<color={normalized_color}>{new_text}</color>'

    @staticmethod
    def apply_color_to_text(doc, page, text, bbox, color):
        """Apply color to text in PDF"""
        try:
            page = doc[page]
            x0, y0, x1, y1 = bbox
            
            # White out original text
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Ensure color is properly normalized
            if isinstance(color, (list, tuple)) and len(color) >= 3:
                if any(c > 1 for c in color):
                    color = [c/255 for c in color[:3]]
            else:
                color = [0, 0, 0]  # Default to black
            
            # Draw colored text
            page.insert_text(
                point=(x0, y1 - 2),  # Adjust Y position
                text=text,
                fontname="helv",  # Use basic font for colored text
                fontsize=y1 - y0,  # Calculate font size from bbox
                color=color
            )
            return True
        except Exception as e:
            print(f"Color application error: {e}")
            return False
