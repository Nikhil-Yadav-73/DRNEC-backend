from django.contrib import admin
from .models import Note, Post, Item, Cart, CartItem, Category, UserProfile, Query

admin.site.register(Note)
admin.site.register(Post)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Query)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(UserProfile)