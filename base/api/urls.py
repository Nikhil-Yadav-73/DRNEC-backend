from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.routes),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('items/', views.ItemListView.as_view(), name='item_list_view'),
    path('items/<int:id>', views.ItemDetailView.as_view(), name='items_detail'),
    path('items/recommended/<int:id>', views.RecommendedItems.as_view(), name='recommended_items'),
    path('categories/', views.CategoryListView.as_view(), name='category_list_view'),
    path('categories/<str:name>', views.CategoryItemListView.as_view(), name='category_items_view'),
    path('cart/<int:id>', views.CartView.as_view(), name='cart_view'), 
    path('userprofile/<int:id>', views.UserProfileView.as_view(), name='user_profile'),
    path('search_items/', views.SearchItems.as_view(), name='search_items'),
    path('search_categories/', views.SearchCategories.as_view(), name='search_categories'),
    path('search_posts/', views.SearchPosts.as_view(), name='search_posts'),
    path('items/add_to_cart/<int:id>/<int:pk>', views.AddToCartView.as_view(), name='add_to_cart'),
    path('items/delete_cart_item/<int:id>/<int:pk>', views.DeleteCartItem.as_view(), name='delete_cart_item'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('update_cartitem_quantity/<int:id>/<str:act>/<int:user_id>', views.UpdateCartItemQuantity.as_view()),
    path('posts/', views.PostsView.as_view()),
    path('like_post/<int:id>/<int:pk>', views.LikePost.as_view()),
    path('new_post/<int:id>', views.NewPost.as_view()),
    path('delete_post/<int:pk>', views.deletePost.as_view()),
    path('update_post/<int:pk>', views.updatePost.as_view()),
    path('edit_profile/<int:pk>', views.EditProfile.as_view()),
    path("edit_post/<int:id>", views.EditPost.as_view()),
    path("checkout", views.Checkout.as_view()),

    path('notes', views.getnotes),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
