import re
from fitz import Document

class LinkHandler:
    # Regular expressions for links and emails
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    @staticmethod
    def is_link_text(text):
        """Check if text contains URL or email"""
        return bool(LinkHandler.URL_PATTERN.search(text) or 
                   LinkHandler.EMAIL_PATTERN.search(text))

    @staticmethod
    def preserve_link_on_edit(original_text, new_text):
        """Preserve link functionality when editing"""
        if not LinkHandler.is_link_text(original_text):
            return new_text
            
        # Keep link attributes if new text is also a valid link
        if LinkHandler.is_link_text(new_text):
            return f'<link>{new_text}</link>'
        return new_text

    @staticmethod
    def apply_link_to_text(doc, page, text, bbox, original_color=None):
        """Apply link formatting to text in PDF with original color"""
        try:
            page = doc[page]
            x0, y0, x1, y1 = bbox
            
            # Use original color for email, standard blue for URLs
            if '@' in text:
                # Normalize original color if provided, otherwise use black
                color = [c/255 if c > 1 else c for c in original_color[:3]] if original_color else (0, 0, 0)
            else:
                # Standard browser link blue for URLs
                color = (0, 0, 0.93)
            
            # White out original text
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Get font size from bbox height
            font_size = y1 - y0
            
            # Draw text
            page.insert_text(
                point=(x0, y1),
                text=text,
                color=color,
                fontsize=font_size
            )
            
            # Add underline
            text_width = page.get_text_width(text, fontsize=font_size)
            page.draw_line(
                start=(x0, y1 + 1),
                end=(x0 + text_width, y1 + 1),
                color=color,
                width=0.5
            )
            
            return True
        except Exception as e:
            print(f"Link application error: {e}")
            return False
