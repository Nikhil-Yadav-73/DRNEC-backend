from rest_framework import serializers
from base.models import Note, Item, Category, Cart, CartItem, UserProfile, Post
from django.contrib.auth.models import User

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'user',
            'text',
            'created_at',
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name'] 

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    image = serializers.ImageField(required=False)

    class Meta:
        model = Item
        fields = [
            'id', 'category', 'name', 'description', 'price',
            'image', 'video', 'created_at', 'quantity',
            'material', 'size'
        ]
    
    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category, created = Category.objects.get_or_create(**category_data)
        item = Item.objects.create(category=category, **validated_data)
        return item
    
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CartItem
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
    
    