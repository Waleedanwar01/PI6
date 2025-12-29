from .models import SiteConfiguration, Page, BlogCategory, BlogPost

def site_config(request):
    try:
        config = SiteConfiguration.objects.first()
    except Exception:
        config = None
    
    # Fetch active footer pages
    try:
        active_pages = Page.objects.filter(is_active=True, show_in_footer=True)
    except Exception:
        active_pages = Page.objects.none()
    
    # Fetch navbar categories (only top-level)
    try:
        navbar_categories = BlogCategory.objects.filter(show_in_navbar=True, parent__isnull=True).prefetch_related('subcategories')
    except Exception:
        navbar_categories = BlogCategory.objects.none()

    # Fetch 'Texas Insurance Resources' category and posts for footer
    try:
        resources_category = BlogCategory.objects.get(name='Texas Insurance Resources')
        resources_posts = BlogPost.objects.filter(category=resources_category, is_published=True).order_by('-published_at')[:5]
    except Exception:
        resources_category = None
        resources_posts = []
    
    # Group by category
    footer_links = {
        'company': active_pages.filter(category='company') if active_pages is not None else [],
        'legal': active_pages.filter(category='legal') if active_pages is not None else [],
        'resources_posts': resources_posts,
        'resources_category': resources_category,
    }
    
    return {
        'site_config': config,
        'footer_links': footer_links,
        'navbar_categories': navbar_categories,
    }
