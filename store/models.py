from unicodedata import category
from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account

# Create your models here.
class Product(models.Model):
    product_name  = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    crated_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def _str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    

# class VariationManager(models.Manager):
#     def colors(self):
#         return super(VariationManager, self ).filter(variation_category= 'color' , is_active=True)


# variation_category_choice = (
#     ('color', 'color'),
     

# class Variation(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE) 
#     variation_category = models.CharField(max_length=100, choices=variation_category_choice)
#     variation_value = models.CharField(max_length=100)
#     is_active  = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now=True)

#     objects = VariationManager()

#     def __unicode__(self):
#         return self.product      

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)