from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return self.title

