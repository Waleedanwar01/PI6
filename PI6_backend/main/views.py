from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Page, BlogPost, BlogCategory, InsurerBrand, QuoteOffer
from .forms import ContactForm

# Create your views here.
def home(request):
    try:
        featured_categories = BlogCategory.objects.filter(is_featured_on_home=True).order_by('home_sort_order', 'id')[:3]
    except Exception:
        featured_categories = []
    try:
        brands_qs = InsurerBrand.objects.filter(is_active=True, show_on_home=True, ranking__gt=0)
        brands = sorted(list(brands_qs), key=lambda b: (b.ranking or 999999, b.name.lower()))
    except Exception:
        brands = []
    return render(request, 'home.html', {'featured_categories': featured_categories, 'brands': brands})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'page_detail.html', {'page': page})

def blog_list(request):
    posts_list = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    # Get only top-level categories and prefetch subcategories
    categories = BlogCategory.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    
    paginator = Paginator(posts_list, 9) # Show 9 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/blog_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'title': 'Latest Articles'
    })

def blog_category_list(request, category_slug):
    category = get_object_or_404(BlogCategory, slug=category_slug)
    
    # Get posts from this category AND all its sub-categories (recursive)
    descendants = category.get_descendants()
    category_ids = [category.id] + [c.id for c in descendants]
    
    posts_list = BlogPost.objects.filter(
        is_published=True, 
        category__id__in=category_ids
    ).order_by('-published_at')
    
    # Get only top-level categories and prefetch subcategories for sidebar
    categories = BlogCategory.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    
    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/blog_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'title': category.name  # Just the name, or "All Products" if you prefer
    })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # 1. Primary Strategy: Same Category
    same_category_posts = BlogPost.objects.filter(
        category=post.category, 
        is_published=True
    ).exclude(id=post.id).order_by('-published_at')
    
    # 2. Secondary Strategy: Other Categories (Recent)
    other_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id).exclude(category=post.category).order_by('-published_at')
    
    # Combine results
    # We want up to 8 posts total (3 for cards, 5 for links)
    recommended_posts = list(same_category_posts[:8])
    
    if len(recommended_posts) < 8:
        needed = 8 - len(recommended_posts)
        recommended_posts.extend(list(other_posts[:needed]))
    
    related_posts = recommended_posts[:3]
    related_links = recommended_posts[3:8]
    
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
        'related_links': related_links
    })

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'There was an error sending your message. Please check the form and try again.')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def start(request):
    # Simple session-based wizard
    wizard = request.session.get('wizard', {})
    step = request.GET.get('step') or request.POST.get('step') or 'address'
    if request.method == 'POST':
        if step == 'address':
            wizard['address'] = (request.POST.get('address') or '').strip()
            request.session['wizard'] = wizard
            return redirect('/start/?step=name')
        elif step == 'name':
            wizard['first_name'] = (request.POST.get('first_name') or '').strip()
            wizard['last_name'] = (request.POST.get('last_name') or '').strip()
            request.session['wizard'] = wizard
            return redirect('/start/?step=email')
        elif step == 'email':
            wizard['email'] = (request.POST.get('email') or '').strip()
            request.session['wizard'] = wizard
            return redirect('/start/?step=phone')
        elif step == 'phone':
            wizard['phone'] = (request.POST.get('phone') or '').strip()
            request.session['wizard'] = wizard
            return redirect('/start/?step=quotes')
        elif step == 'reset':
            request.session['wizard'] = {}
            return redirect('/start/')
    try:
        brands = InsurerBrand.objects.filter(is_active=True, show_on_home=True).order_by('ranking', 'name')
    except Exception:
        brands = []
    offers = []
    if step == 'quotes':
        try:
            offers = QuoteOffer.objects.filter(is_active=True).order_by('order', 'id').prefetch_related('brands')
        except Exception:
            offers = []
    return render(request, 'start.html', {'brands': brands, 'step': step, 'wizard': wizard, 'offers': offers, 'product': 'home'})

def start_auto(request):
    # Auto flow reusing the same wizard pattern
    wizard = request.session.get('wizard_auto', {})
    step = request.GET.get('step') or request.POST.get('step') or 'address'
    if request.method == 'POST':
        if step == 'address':
            wizard['address'] = (request.POST.get('address') or '').strip()
            request.session['wizard_auto'] = wizard
            return redirect('/start-auto/?step=name')
        elif step == 'name':
            wizard['first_name'] = (request.POST.get('first_name') or '').strip()
            wizard['last_name'] = (request.POST.get('last_name') or '').strip()
            request.session['wizard_auto'] = wizard
            return redirect('/start-auto/?step=email')
        elif step == 'email':
            wizard['email'] = (request.POST.get('email') or '').strip()
            request.session['wizard_auto'] = wizard
            return redirect('/start-auto/?step=phone')
        elif step == 'phone':
            wizard['phone'] = (request.POST.get('phone') or '').strip()
            request.session['wizard_auto'] = wizard
            return redirect('/start-auto/?step=quotes')
        elif step == 'reset':
            request.session['wizard_auto'] = {}
            return redirect('/start-auto/')
    try:
        brands = InsurerBrand.objects.filter(is_active=True, show_on_home=True).order_by('ranking', 'name')
    except Exception:
        brands = []
    offers = []
    if step == 'quotes':
        try:
            offers = QuoteOffer.objects.filter(is_active=True).order_by('order', 'id').prefetch_related('brands')
        except Exception:
            offers = []
    return render(request, 'start.html', {'brands': brands, 'step': step, 'wizard': wizard, 'offers': offers, 'product': 'auto'})

def companies(request):
    company_category = BlogCategory.objects.filter(slug='companies').first()
    if not company_category:
        company_category = BlogCategory.objects.filter(name__iexact='companies', parent__isnull=True).first()
    if company_category:
        company_subcategories = company_category.subcategories.all()
        brand_qs = InsurerBrand.objects.filter(is_active=True, show_in_companies=True, ranking__gt=0)
        brand_map = {b.name.lower(): b for b in brand_qs}
        company_subcategories = [sub for sub in company_subcategories if sub.name.lower() in brand_map]
        company_subcategories.sort(key=lambda s: (brand_map[s.name.lower()].ranking, s.name.lower()))
    else:
        company_subcategories = []
    try:
        brands = InsurerBrand.objects.filter(
            is_active=True,
            show_in_companies=True,
            ranking__gt=0
        ).order_by('ranking', 'name')
    except Exception:
        brands = []
    page_obj = None
    selected_title = None
    posts_list = None
    category_slug = request.GET.get('category')
    brand_id = request.GET.get('brand')
    base_query = ''
    if category_slug:
        category = BlogCategory.objects.filter(slug=category_slug).first()
        if category:
            descendants = category.get_descendants()
            category_ids = [category.id] + [c.id for c in descendants]
            posts_list = BlogPost.objects.filter(
                is_published=True,
                category__id__in=category_ids
            ).order_by('-published_at')
            selected_title = category.name
            base_query = f'category={category_slug}'
    elif brand_id:
        try:
            brand = InsurerBrand.objects.get(id=brand_id)
            posts_list = BlogPost.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=brand.name) | Q(content__icontains=brand.name)
            ).order_by('-published_at')
            selected_title = brand.name
            base_query = f'brand={brand_id}'
        except InsurerBrand.DoesNotExist:
            pass
    if posts_list is not None:
        paginator = Paginator(posts_list, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request, 'companies.html', {
        'brands': brands,
        'company_category': company_category,
        'company_subcategories': company_subcategories,
        'page_obj': page_obj,
        'selected_title': selected_title,
        'base_query': base_query
    })

def company_blogs(request, brand_id):
    brand = get_object_or_404(InsurerBrand, id=brand_id)
    posts_list = BlogPost.objects.filter(
        is_published=True
    ).filter(
        Q(title__icontains=brand.name) | Q(content__icontains=brand.name)
    ).order_by('-published_at')
    categories = BlogCategory.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/blog_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'title': f'{brand.name} Articles'
    })

def api_health(request):
    try:
        count = InsurerBrand.objects.count()
        return JsonResponse({'db': 'ok', 'brands_count': count})
    except Exception:
        return JsonResponse({'db': 'error', 'brands_count': 0}, status=503)
