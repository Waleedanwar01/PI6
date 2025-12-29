from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import SiteConfiguration, Page, ContactMessage, InsurerBrand, QuoteOffer
 

class SingletonModelAdmin(admin.ModelAdmin):
    """
    Prevents adding new instances if one already exists.
    """
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin, admin.ModelAdmin):
    fieldsets = (
        ('General Info', {
            'fields': ('site_name', 'site_email', 'site_phone', 'site_address', 'copyright_text')
        }),
        ('Home Page Hero & SEO', {
            'fields': ('home_page_title', 'home_page_description'),
            'description': "Manage the Title and Description for both the Home Page Hero section and SEO Meta tags."
        }),
        ('Start Page Wizard', {
            'fields': ('wizard_final_screenshot_url',),
            'description': "Set the final screenshot image shown after the user completes the Start page steps."
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url')
        }),
    )

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'show_in_footer', 'updated_at')
    list_filter = ('category', 'is_active', 'show_in_footer')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Page Info', {
            'fields': ('title', 'slug', 'category', 'is_active', 'show_in_footer'),
            'description': "Basic page information. Slug is auto-generated from Title."
        }),
        ('Hero Section', {
            'fields': ('hero_title',),
            'description': "Settings for the top hero banner."
        }),
        ('Content', {
            'fields': ('content',),
            'description': "Main page content."
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description'),
            'description': "Search Engine Optimization settings."
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
admin.site.site_header = "Texas Insurance Ratings Admin"
admin.site.site_title = "Texas Insurance Ratings Admin"
admin.site.index_title = "Administration"

@admin.register(InsurerBrand)
class InsurerBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'ranking', 'complaint_score', 'rating_stars', 'show_in_companies', 'show_on_home', 'logo_preview', 'is_active')
    list_filter = ('is_active', 'show_in_companies', 'show_on_home')
    search_fields = ('name',)
    list_editable = ('ranking', 'show_in_companies', 'show_on_home')
    
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="height:30px;"/>')
        return "—"
    logo_preview.short_description = 'Logo'
    
    def rating_stars(self, obj):
        if obj.rating:
            stars = '★' * int(obj.rating)
            empty = '☆' * (5 - int(obj.rating))
            return f'{stars}{empty}'
        return "—"
    rating_stars.short_description = 'Rating'

@admin.register(QuoteOffer)
class QuoteOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'premium', 'phone', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'premium', 'phone')
    list_editable = ('order', 'is_active')
    filter_horizontal = ('brands',)
