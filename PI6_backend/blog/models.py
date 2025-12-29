from django.db import models
from main.models import BlogPost as OriginalBlogPost
from main.models import BlogCategory as OriginalBlogCategory

class BlogPost(OriginalBlogPost):
    class Meta:
        proxy = True
        app_label = 'blog'
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

class BlogCategory(OriginalBlogCategory):
    class Meta:
        proxy = True
        app_label = 'blog'
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

