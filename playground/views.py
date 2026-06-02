from itertools import count
from django.db.models.aggregates import Count
from django.shortcuts import render
from django.db.models.expressions import F
from store.models import Product, Order, Customer, Promotion, Collection
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem
from django.db.models import Manager, Func, ExpressionWrapper, DecimalField, IntegerField


def say_hello(request):
    products = Product.objects.select_related('collection').prefetch_related('promotion').annotate(
        discounted_price = ExpressionWrapper(F('unit_price') - F('unit_price') * F('promotion__discount') / 100, output_field=DecimalField(max_digits=6, decimal_places=3))
    )
    # I want above discounted_price be rounded
    qs = Product.objects.filter(inventory__gt = F('unit_price'))
    query_set = Order.objects.select_related('customer').prefetch_related('order_item__product').order_by('-place_at')[:15]
    tags = TaggedItem.objects.get_tags_for(Product, 12)
    product_count = Collection.objects.annotate(product_count=Count('product')).order_by('id')
    # I want to get discount from Promotion model, then calculate discounted_price

    return render(request, 'hello.html', {'name': 'there', 'products': products, 'orders': query_set, 'tags': list(tags), 'counts': list(product_count), 'rela': list(qs)})