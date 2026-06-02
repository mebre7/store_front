from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

carts_router = routers.NestedDefaultRouter(router, r'carts', lookup='cart')
carts_router.register(r'items', views.CartItemViewSet, basename='cart-items')
urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(carts_router.urls)),
]
