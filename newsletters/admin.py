from django.contrib import admin
from .models import Newsletter

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_date")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "author")
    ordering = ("-published_date",)
