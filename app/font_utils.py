from app.config import Config

def get_fallback_font(original_font):
    """
    Get appropriate fallback font based on original font characteristics
    """
    # Try to preserve exact font name if it matches pattern
    if any(std in original_font for std in ['Times', 'Helvetica', 'Courier']):
        return original_font
        
    if original_font in Config.STANDARD_FONTS:
        return original_font
        
    # More specific font matching
    if 'Bold' in original_font and 'Italic' in original_font:
        if 'Times' in original_font:
            return 'Times-BoldItalic'
        return 'Helvetica-BoldOblique'
    elif 'Bold' in original_font:
        if 'Times' in original_font:
            return 'Times-Bold'
        return 'Helvetica-Bold'
    elif 'Italic' in original_font or 'Oblique' in original_font:
        if 'Times' in original_font:
            return 'Times-Italic'
        return 'Helvetica-Oblique'
        
    return Config.DEFAULT_FONT

def preserve_text_attributes(span):
    """
    Extract text attributes from a text span
    """
    return {
        'font': span.get('font', Config.DEFAULT_FONT),
        'size': span.get('size', 12),
        'color': span.get('color', (0, 0, 0)),
        'flags': span.get('flags', 0),  # Contains bold, italic, etc.
        'bbox': span.get('bbox', None),
    }
