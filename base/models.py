from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

now = timezone.now() 
  
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=254)
    user_id = models.IntegerField(default=1)
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        ordering = ('created_at',)
        
    def __str__(self):
        return self.title 
  
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, blank=True)
    pfp = models.ImageField(upload_to='user_pfp', blank=True, null=True)
    liked_posts = models.ManyToManyField(Post, related_name='liked_by_users', blank=True)
    phone = models.CharField(max_length=15, default='1234567890')
    is_verified = models.BooleanField(default=False)
    city = models.CharField(max_length=30, default="Jaipur")
    state = models.CharField(max_length=30, default="Rajasthan")
    country = models.CharField(max_length=30, default="Bharat")
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.user.username
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.username

    
sizes = [
    ("small","Small"),
    ("medium","Medium"),
    ("large","Large"),
    ("xlarge","Xlarge"),
    ("xxlarge","XXlarge"),
]  

gender_choices = [
    ('men', 'Men'),
    ('women', 'Women'),
    ('girls', 'Girls'),
    ('boys', 'Boys'),
    ('all', 'All'),
]

class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()    
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)   
    quantity = models.PositiveIntegerField(default=1) 
    material = models.CharField(null=True, blank=True, max_length=50)
    size = models.CharField(choices=sizes, max_length=15, blank=True, null=True)            
    gender = models.CharField(choices=gender_choices, max_length=10, default="all")
    
    class Meta:
        ordering = ('created_at',)
        
    def __str__(self):
        return self.name 
    
class Query(models.Model):
    name = models.CharField(max_length=255)
    message = models.TextField(blank=False, null=False)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('created_at',)
        
    def __str__(self):
        return self.name 


transaction_status = [
    ("pending","Pending"),
    ("failed","Failed"),
    ("success","Success")
]

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    items = models.ManyToManyField(Item, through='CartItem')
    
    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = 'Cart'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.item.name

class Note(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, related_name='notes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(f"User: {self.user}_____created at: {self.created_at}")