from django.contrib import admin
from .models import BlogPost, BlogCategory
from main.models import BlogGalleryImage

class BlogGalleryImageInline(admin.TabularInline):
    model = BlogGalleryImage
    extra = 1
    fields = ('image', 'caption', 'order')

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'show_in_navbar', 'has_dropdown', 'slug', 'created_at')
    list_filter = ('parent', 'show_in_navbar', 'has_dropdown')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('show_in_navbar', 'has_dropdown')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'published_at', 'updated_at')
    list_filter = ('category', 'is_published', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BlogGalleryImageInline]
    
    fieldsets = (
        ('Article Info', {
            'fields': ('title', 'slug', 'category', 'featured_image', 'excerpt'),
        }),
        ('Content', {
            'fields': ('content',),
        }),
        ('Optional Content', {
            'fields': ('video_url', 'video_file', 'button_text', 'button_url'),
            'description': "Add a video or a Call-to-Action button to the blog post."
        }),
        ('Publishing', {
            'fields': ('is_published',),
            'description': "Uncheck to save as draft."
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description'),
        }),
    )
