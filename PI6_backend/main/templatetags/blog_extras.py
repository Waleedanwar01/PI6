from django import template
import hashlib

register = template.Library()

@register.filter
def get_random_image(value):
    """
    Returns a deterministic random image URL using LoremFlickr with a lock based on the input value.
    This ensures each post gets a unique but consistent image related to business/office.
    Usage: {{ post.id|get_random_image }}
    """
    if not value:
        # Default fallback
        return "https://loremflickr.com/800/600/business,office?lock=1"
    
    try:
        # Create a deterministic hash of the value (e.g. post ID or slug)
        hash_object = hashlib.md5(str(value).encode())
        hash_int = int(hash_object.hexdigest(), 16)
        
        # Use modulo to get a lock ID between 1 and 1000
        # This ensures we get varied images but consistent for the same post
        lock_id = (hash_int % 1000) + 1
        
        return f"https://loremflickr.com/800/600/business,office?lock={lock_id}"
    except Exception:
        return "https://loremflickr.com/800/600/business,office?lock=1"

@register.filter
def get_auto_image(value):
    """
    Returns a deterministic auto-themed image URL using LoremFlickr with car/auto tags.
    Black & white styling should be applied via CSS classes in templates.
    Usage: {{ brand.id|get_auto_image }} or {{ any_value|get_auto_image }}
    """
    if not value:
        return "https://loremflickr.com/800/600/car,auto?lock=1"
    try:
        hash_object = hashlib.md5(str(value).encode())
        hash_int = int(hash_object.hexdigest(), 16)
        lock_id = (hash_int % 1000) + 1
        return f"https://loremflickr.com/800/600/car,auto?lock={lock_id}"
    except Exception:
        return "https://loremflickr.com/800/600/car,auto?lock=1"
