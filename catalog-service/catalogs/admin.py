from django.contrib import admin
from .models import BookCategory, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'category')
    list_filter = ('category',)
    search_fields = ('book_id',)
