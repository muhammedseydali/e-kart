from django.db import models
from django.urls import reverse


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cate_image = models.ImageField(upload_to='photos/categories', blank=True)

# THIS IS USED FOR SHOWING THE NAME IN VERBOSE NAME FROMAT
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.category_name


    def get_url(self):
        return reverse('products_by_category', args=[self.slug])    