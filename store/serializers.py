from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        read_only_fields = ['id', 'products_count']
    
    products_count = serializers.IntegerField(read_only=True)
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)

# model serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =[
            'id',
            'title',
            'slug',
            'description',
            'inventory',
            'price',
            'price_with_tax',
            'collection',
            'collection_id',
            'is_available',
        ]
    # if you want to rename 'unit_price' ro 'price'
    price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        source='unit_price',
        coerce_to_string=False,
    )
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset = Collection.objects.all(),
    #     view_name='collection-detail',
    #     lookup_url_kwarg = 'id'
    # )
    collection = serializers.StringRelatedField(read_only=True)
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source='collection',
        write_only=True,
        required=False,
        allow_null=True,
    )
    is_available = serializers.SerializerMethodField()
    # define what price_with_tax method is
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self, product):
        return product.unit_price * Decimal(1.1)

    def get_is_available(self, product):
        return product.inventory > 0

class CartItemProductSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'total_price']
    unit_price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        source='product.unit_price',
        read_only=True,
        coerce_to_string=False
    )
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance
    
    # validations methods
    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('Invalid Product ID')
        return value
    
    # def validate_quantity(self, value):
    #     if value <= 0:
    #         raise serializers.ValidationError('Quantity must be greater than 0.')
    #     return value
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    def get_total_price(self, cart: Cart):
        return sum(item.quantity * item.product.unit_price for item in cart.items.all())


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 'membership']
        read_only_fields = ['id', 'membership']


class OrderItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'line_total']

    line_total = serializers.SerializerMethodField()

    def get_line_total(self, item):
        return item.quantity * item.unit_price


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(source='order_item', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    payment_status_label = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'place_at', 'payment_status', 'payment_status_label', 'customer', 'items', 'total_price']

    def get_total_price(self, order):
        return sum(item.quantity * item.unit_price for item in order.order_item.all())


class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=255, allow_blank=True, required=False)

    def validate_cart_id(self, value):
        cart = Cart.objects.filter(pk=value).prefetch_related('items__product').first()
        if not cart:
            raise serializers.ValidationError('Cart not found.')
        if not cart.items.exists():
            raise serializers.ValidationError('Cart is empty.')
        for item in cart.items.all():
            if item.product.inventory < item.quantity:
                raise serializers.ValidationError(f'{item.product.title} does not have enough inventory.')
        self.context['cart'] = cart
        return value

    @transaction.atomic
    def create(self, validated_data):
        cart = self.context['cart']
        customer, _ = Customer.objects.update_or_create(
            email=validated_data['email'],
            defaults={
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'phone': validated_data.get('phone', ''),
            },
        )
        order = Order.objects.create(customer=customer)
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.unit_price,
            )
            for item in cart.items.select_related('product')
        ]
        OrderItem.objects.bulk_create(order_items)

        for item in cart.items.select_related('product'):
            product = item.product
            product.inventory -= item.quantity
            product.save(update_fields=['inventory', 'last_update'])

        cart.delete()
        return order
