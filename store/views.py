from django.db.models.aggregates import Count
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, SAFE_METHODS
from rest_framework.response import Response
from .models import Cart, CartItem, Collection, Order, Product
from store.serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    CollectionSerializer,
    OrderSerializer,
    ProductSerializer,
    UpdateCartItemSerializer,
)
from rest_framework import generics, mixins, viewsets

class IsAdminOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or super().has_permission(request, view)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.select_related('collection').all()
        search = self.request.query_params.get('search')
        collection = self.request.query_params.get('collection')
        available = self.request.query_params.get('available')

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if collection:
            queryset = queryset.filter(collection_id=collection)
        if available in {'1', 'true', 'True'}:
            queryset = queryset.filter(inventory__gt=0)
        return queryset


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Collection.objects.annotate(products_count=Count('products')).all()

class CartViewSet(
                mixins.CreateModelMixin, 
                mixins.RetrieveModelMixin, 
                mixins.DestroyModelMixin, 
                viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order, context={'request': request}).data, status=201)

class CartItemViewSet(viewsets.ModelViewSet):
    # queryset = CartItem.objects.all()
    # serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem\
            .objects\
            .filter(cart_id=self.kwargs['cart_pk'])\
            .select_related('product')


class OrderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        email = self.request.query_params.get('email')
        queryset = Order.objects.select_related('customer').prefetch_related('order_item__product').all()
        if email:
            queryset = queryset.filter(customer__email__iexact=email)
        return queryset.order_by('-place_at')
