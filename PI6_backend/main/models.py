from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

def generate_unique_slug(instance, source_value, slug_field_name='slug'):
    """
    Generates a unique slug for a model instance.
    """
    slug = slugify(source_value)
    unique_slug = slug
    ModelClass = instance.__class__
    num = 1
    
    while ModelClass.objects.filter(**{slug_field_name: unique_slug}).exclude(pk=instance.pk).exists():
        unique_slug = f'{slug}-{num}'
        num += 1
        
    return unique_slug

class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=255, default="Texas Insurance Ratings")
    site_email = models.EmailField(default="contact@example.com")
    site_phone = models.CharField(max_length=50, default="(123) 456-7890")
    site_address = models.TextField(default="708 Main Street\nHouston, TX 77002")
    copyright_text = models.CharField(max_length=255, default="© 2024 Texas Insurance Ratings. All rights reserved.", help_text="Footer copyright text")
    
    # Home Page SEO
    home_page_title = models.CharField(max_length=255, default="Compare <span style='color: #ffcc00; font-style: italic;'>Texas Insurance Rates</span>", help_text="Used for both SEO Meta Title and Hero Section Title. Use <span style='color: #ffcc00; font-style: italic;'>text</span> for yellow italic styling.")
    home_page_description = models.TextField(default="Compare Texas Insurance Rates for Home, Auto, and Renters.", help_text="Used for both SEO Meta Description and Hero Section Description")

    # Start Page Wizard
    wizard_final_screenshot_url = models.URLField(blank=True, null=True, help_text="URL of the final quotes screenshot shown after wizard completion")

    # Social Links
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

class Page(models.Model):
    class Meta:
        verbose_name = "Company & Legal Page"
        verbose_name_plural = "Company & Legal Pages"

    CATEGORY_CHOICES = [
        ('company', 'Company'),
        ('legal', 'Legal'),
    ]

    title = models.CharField(max_length=200, help_text="This will be used as the page name and slug.")
    slug = models.SlugField(unique=True, blank=True)
    
    # Hero Section
    hero_title = models.CharField(max_length=200, blank=True, help_text="Title to display in the Hero section")
    
    # Content
    content = RichTextField(help_text="Full clean editor with all options.")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO Meta Description")
    
    # Footer Settings
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='company', help_text="Section in the footer where this page should appear")
    is_active = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True, help_text="Show this page link in the footer")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Always ensure a slug is generated from the title if missing,
        # or from the existing slug if present (to handle edits safely)
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        else:
            # Re-verify uniqueness even if slug exists (e.g. manual edit conflict)
            self.slug = generate_unique_slug(self, self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name}"

# Blog Models
class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', help_text="Select a parent category if this is a sub-category")
    description = models.TextField(blank=True)
    
    # Navigation Settings
    show_in_navbar = models.BooleanField(default=False, help_text="Show this category in the main navigation menu")
    has_dropdown = models.BooleanField(default=False, help_text="If checked, hovering this link will show latest 5 blog posts from this category")
    
    # Home Page Feature Fields
    is_featured_on_home = models.BooleanField(default=False, help_text="Check to display this category on the home page top section")
    home_title = models.CharField(max_length=100, blank=True, help_text="Override name for home page display")
    home_description = models.TextField(blank=True, help_text="Description for home page")
    home_cta_text = models.CharField(max_length=200, blank=True, help_text="Button text for home page")
    home_cta_url = models.CharField(max_length=200, blank=True, help_text="Custom URL (optional)")
    home_sort_order = models.IntegerField(default=0, help_text="Order of display on home page")
    icon_svg = models.TextField(blank=True, help_text="Paste SVG code here")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        else:
            self.slug = generate_unique_slug(self, self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def get_descendants(self):
        """
        Recursively get all descendant categories.
        """
        descendants = []
        children = self.subcategories.all()
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_family_posts(self):
        """
        Returns the latest 5 published posts from this category AND its subcategories (recursive).
        """
        categories = [self] + self.get_descendants()
        return BlogPost.objects.filter(
            category__in=categories,
            is_published=True
        ).order_by('-published_at')[:5]

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    
    # Content
    excerpt = models.TextField(blank=True, help_text="Short summary for the blog list page")
    content = RichTextField()
    featured_image = CloudinaryField('image', folder='blog_images', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Optional: YouTube/Vimeo URL to display in the post")
    video_file = models.FileField(upload_to='blog_videos/', blank=True, null=True, help_text="Optional: Upload a video file from your device")
    
    # Optional Button
    button_text = models.CharField(max_length=50, blank=True, help_text="Optional: Text for a Call-to-Action button")
    button_url = models.URLField(blank=True, null=True, help_text="Optional: URL for the Call-to-Action button")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO Meta Description")

    # Status
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        # Always ensure a slug is generated from the title if missing,
        # or from the existing slug if present (to handle edits safely)
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        else:
            # Re-verify uniqueness even if slug exists (e.g. manual edit conflict)
            self.slug = generate_unique_slug(self, self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogGalleryImage(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='gallery_images')
    image = CloudinaryField('image', folder='blog_gallery')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return f"Image for {self.blog_post.title}"

class InsurerBrand(models.Model):
    name = models.CharField(max_length=100)
    logo = CloudinaryField('image', folder='logos', blank=True, null=True)
    hover_color = models.CharField(max_length=7, blank=True)
    is_active = models.BooleanField(default=True)
    ranking = models.PositiveIntegerField(default=0)
    complaint_score = models.FloatField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, help_text="1-5 stars")
    show_in_companies = models.BooleanField(default=True, help_text="Show in Companies categories/table")
    show_on_home = models.BooleanField(default=False, help_text="Show brand on home/start page logos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Insurer Brand"
        verbose_name_plural = "Insurer Brands"
        ordering = ['ranking', 'name']

    def __str__(self):
        return self.name

class QuoteOffer(models.Model):
    brands = models.ManyToManyField(InsurerBrand, blank=True, related_name='offers')
    title = models.CharField(max_length=200)
    premium = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True)
    cta_text = models.CharField(max_length=100, default='Call Now')
    cta_url = models.URLField(blank=True)
    highlight = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Quote Offer"
        verbose_name_plural = "Quote Offers"
    
    def __str__(self):
        return self.title
