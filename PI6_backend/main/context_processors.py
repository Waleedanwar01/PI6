from django.core.cache import cache
from .models import SiteConfiguration, Page, BlogCategory, BlogPost

def site_config(request):
    try:
        config = cache.get('site_config')
        if config is None:
            config = SiteConfiguration.objects.first()
            cache.set('site_config', config, 300)
    except Exception:
        config = None
    
    # Fetch active footer pages
    try:
        active_pages = Page.objects.filter(is_active=True, show_in_footer=True)
    except Exception:
        active_pages = Page.objects.none()
    
    # Fetch navbar categories (only top-level)
    try:
        navbar_categories = cache.get('navbar_categories')
        if navbar_categories is None:
            navbar_qs = BlogCategory.objects.filter(show_in_navbar=True, parent__isnull=True).prefetch_related('subcategories')
            navbar_categories = list(navbar_qs)
            cache.set('navbar_categories', navbar_categories, 300)
    except Exception:
        navbar_categories = []

    # Fetch 'Texas Insurance Resources' category and posts for footer
    try:
        resources_category = cache.get('resources_category')
        resources_posts = cache.get('resources_posts')
        if resources_posts is None or resources_category is None:
            resources_category = BlogCategory.objects.get(name='Texas Insurance Resources')
            resources_posts = list(BlogPost.objects.filter(category=resources_category, is_published=True).order_by('-published_at')[:5])
            cache.set('resources_category', resources_category, 300)
            cache.set('resources_posts', resources_posts, 300)
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
