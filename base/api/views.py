from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from base.models import Note, Item, Cart, CartItem, Category, UserProfile, User, Post
from .serializers import NoteSerializer, ItemSerializer, CategorySerializer, CartItemSerializer, UserSerializer, UserProfileSerializer, PostSerializer
from rest_framework.exceptions import NotFound
from rest_framework import generics, status, pagination
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
import json
from .email import send_update_email

def SendEmail():
    subject = "just a test subject"
    message = "this is just a test message"
    recipents = ['nikhilyadavwork73@gmail.com']
    send_update_email(subject=subject, message=message, recipient_list=recipents)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def routes(request):
    routes = [
        '/api/token/refresh',
        '/api/token/',
    ]

    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getnotes(request):
    notes = Note.objects.filter(user=request.user)
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

# Core

class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_serializer_context(self):
        return {'request': self.request}

# @permission_classes([IsAuthenticated])
class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'id'

    def update(self, request, id, *args, **kwargs):
        try:
            item = Item.objects.get(id=id)
            serializer = ItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Item updated successfully!", "item": serializer.data}, status=status.HTTP_205_RESET_CONTENT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            raise NotFound(detail="Item not found", code=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, *args, **kwargs):
        try:
            item = Item.objects.get(id=id)
            item.delete()
            return Response({"message": "Item deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Item.DoesNotExist:
            raise NotFound(detail="Item not found", code=status.HTTP_404_NOT_FOUND)
        
class RecommendedItems(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'id'

    def get(self, request, id, *args, **kwargs):
        try:
            item = Item.objects.get(id=id)
            category = item.category
            recommended_items = Item.objects.filter(category=category).exclude(id=id)[:4]
            serializer = self.get_serializer(recommended_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Item.DoesNotExist:
            raise NotFound(detail="Item not found", code=status.HTTP_404_NOT_FOUND)
        
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

class CategoryItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'id'

    def get(self, request, name, *args, **Kwargs):
        try:
            category = Category.objects.get(name=name)
            items = Item.objects.filter(category=category)
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            raise NotFound(detail="Item not found", code=status.HTTP_404_NOT_FOUND)
 
class CartView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            serializer = self.get_serializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Cart.DoesNotExist:
            return Response({"detail": "Cart is Empty"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'id'

    def get(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            userprofile, created = UserProfile.objects.get_or_create(user=user)
            serializer = self.get_serializer(userprofile)
            user_serializer = UserSerializer(user)
            return Response({"profile":serializer.data,"user_data": user_serializer.data}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            raise NotFound(detail="User not found", code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            userprofile = UserProfile.objects.get(user=user)

            profile_data = json.loads(request.data.get('profile', '{}'))
            user_data = json.loads(request.data.get('user_data', '{}'))

            if user_data:
                user.username = user_data.get("username", user.username)
                user.email = user_data.get("email", user.email)
                userprofile.name = user.username
                user.save()

            if profile_data:
                userprofile.city = profile_data.get('city', userprofile.city)
                userprofile.state = profile_data.get('state', userprofile.state)
                userprofile.country = profile_data.get('country', userprofile.country)
                userprofile.phone = profile_data.get('phone', userprofile.phone)

            if 'pfp' in request.FILES:
                userprofile.pfp = request.FILES['pfp']
            userprofile.save()

            profile_serializer = self.get_serializer(userprofile, data=profile_data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response({
                    "profile": UserProfileSerializer(userprofile).data,
                    "user_data": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            raise NotFound(detail="User not found", code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SearchItems(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = Item.objects.all()
        query = self.request.query_params.get('query', None)
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return queryset
    
class SearchCategories(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        query = self.request.query_params.get('query', None)
        if query:
            queryset = queryset.filter(Q(name__icontains=query))
        return queryset
    
class SearchPosts(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all()
        query = self.request.query_params.get('query', None)
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return queryset
    
class AddToCartView(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'id'

    def post(self, request, id, pk, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            cart, created = Cart.objects.get_or_create(user=user)
            item = Item.objects.get(id=pk)
            try: 
                cart_item = CartItem.objects.get(item=item, cart=cart)
                if cart_item is not None:
                    cart_item.quantity = cart_item.quantity + 1
            except CartItem.DoesNotExist:
                    cart_item = CartItem.objects.create(
                    cart=cart,
                    item=item,
                    quantity = 1
                )
            cart_item.save()

            return Response({'message': 'Item added to cart successfully!'}, status=status.HTTP_201_CREATED)

        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteCartItem(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    lookup_field = 'pk'

    def post(self, request, id, pk, *args, **kwargs):
        try:
            user = User.objects.get(id=id)
            cart = Cart.objects.get(user=user)
            item = Item.objects.get(id=pk)
            cart_item = CartItem.objects.get(item=item, cart=cart)
            cart_item.delete()
            cart.save()

            cart_items = CartItem.objects.filter(cart=cart)
            serializer = self.get_serializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart is Empty"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class Signup(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            userprofile = UserProfile.objects.create(
                name = user.username,
                user=user
            )
            userprofile.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateCartItemQuantity(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer 
    lookup_field = 'id'

    def post(self, request, id, act, user_id, *args, **kwargs):
        try:
            num = int(act)
            user = User.objects.get(id=user_id)
            item = Item.objects.get(id=id)
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(item=item, cart=cart)
            cart_item.quantity = cart_item.quantity + num
            if item.quantity < cart_item.quantity:
                cart_item.quantity = item.quantity
                cart_item.save()
            if cart_item.quantity <= 0:
                cart_item.delete()
            else: cart_item.save()

            cart_items = CartItem.objects.filter(cart=cart)
            serializer = self.get_serializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({'error': 'Cart Item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found (out of stock)'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PostsPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
        
class PostsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Post.objects.all().order_by("-created_at")
    pagination_class = PostsPagination

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
class LikePost(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def post(self, request, id, pk, *args, **kwargs):
        try:
            post = Post.objects.get(id=pk)
            user = User.objects.get(id=id)
            if post.liked_by.filter(id=user.id).exists():
                post.likes = post.likes - 1
                post.liked_by.remove(user)
            else:
                post.likes = post.likes + 1
                post.liked_by.add(user)
            post.save()
            serializer = self.get_serializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        
class NewPost(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def post(self, request, id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            post = serializer.save()
            post.user_id = id
            post.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class deletePost(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(id=pk)
            post.delete()
            posts = Post.objects.all()
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        

class updatePost(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(id=pk)
            posts = Post.objects.all()
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)


class EditProfile(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()


class EditPost(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def put(self, request, id, *args, **kwargs):
        try:
            post = Post.objects.get(id=id)
            post_data = json.loads(request.data.get('post', '{}'))
        
            if 'image' in request.FILES:
                post.image = request.FILES['image']
            post.save()

            serializer = self.get_serializer(post, data=post_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Done!"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Post.DoesNotExist:
            return Response({'error':"post does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":e}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, *args, **kwargs):
        try:
            post = Post.objects.get(id=id)
            serializer = self.get_serializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"error": "Post doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
    