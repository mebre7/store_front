from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import PROTECT
from tags.models import TaggedItem
from django.contrib.contenttypes.fields import GenericRelation
from uuid import uuid4


# django creates ID field automatically. But if we want we can create by using primary_key
class Collection(models.Model):
    title = models.CharField(max_length=255, null=True)
    feature_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')
    def __str__(self) -> str:
        return str(self.title)
    class Meta:
        ordering = ['title']
    # product_set
# class attribute

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    def __str__(self):
        return f'{self.description}'
    class Meta:
        ordering = ['-description']

class Product(models.Model):
    # sku = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField('slug')
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, null=True, blank=True, related_name='products') # null=True is for database and blank=True is for validation in forms of admin site and other forms.
    promotion = models.ManyToManyField(Promotion, blank=True)
    tags = GenericRelation(TaggedItem)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['title']

class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold')
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    class Meta:
        ordering = ['first_name']

class Order(models.Model):
    PAYMENT_PENDING = 'P'
    PAYMENT_COMPLETE = 'C'
    PAYMENT_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_COMPLETE, 'Complete'),
        (PAYMENT_FAILED, 'Failed')
    ]
    place_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices = PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    def __str__(self):
        return f"Payment status: {'Pending' if self.payment_status == 'P' else 'Complete' if self.payment_status == 'C' else 'Failed'}"
    class Meta:
        ordering = ['id']
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='order_item')
    product = models.ForeignKey(Product, on_delete=PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE) # or models.SET_NULL(), SET_DEFAULT(), SET_PROTECT()
    zip = models.CharField(max_length=255, null=True)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    # items

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name = 'items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'product']]
        # 