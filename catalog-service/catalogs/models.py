from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    book_id = models.PositiveBigIntegerField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='book_links')

    class Meta:
        db_table = 'book_categories'
        indexes = [models.Index(fields=['category'])]

    def __str__(self):
        return f'book#{self.book_id} -> {self.category_id}'
