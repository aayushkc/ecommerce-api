from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
urlpatterns = [
     path('products', views.ProductList.as_view(), name='product'),
     path('cart-items', views.CartItem.as_view(), name = 'cart-item'),
     path('add-to-cart/<int:id>', views.AddCartItems.as_view(), name='add-to-cart'),
     path('shipping', views.ShippingDetails.as_view(), name='shipping'),
     
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)