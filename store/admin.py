from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import QuerySet
from django.db.models.aggregates import Count
from django.http import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse


from . import models

class InventoryStatusFilter(admin.SimpleListFilter):
    title = 'inventory status'
    parameter_name = 'inventory_status'

    def lookups(self, request, model_admin):
        return [
            ('0', 'Out of Stock'),
            ('<10', 'Low'),
            ('<50', 'Medium'),
            ('>=50', 'Ok')
        ]
    
    def queryset(self, request: HttpRequest, queryset: QuerySet):
        if self.value() == '0':
            return queryset.filter(inventory=0)
        elif self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '<50':
            return queryset.filter(inventory__lt=50)
        elif self.value() == '>=50':
            return queryset.filter(inventory__gte=50)

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'products_count')
    search_fields = ('title', )

    # This is method overriding.
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection__id': collection.id}) # reverse is used to get the url of the produuct changelist page in the admin site. We adre adding a query parameter to filter the products by collection id.
        return format_html("<a href='{}'>{}</a>", url, collection.products_count)
    

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ('clear_inventory', )
    autocomplete_fields = ('collection', )

    # fields = ['title', 'slug']
    # readonly_fields = ['title']
    # exclude = ['title', 'slug']
    search_fields = ['title']
    list_display = ('title', 'unit_price', 'description', 'discounted_price', 'inventory_status', 'collection_title')
    list_editable = ('unit_price', )
    list_per_page = 100
    list_select_related = ('collection', )
    list_filter = ('collection', 'last_update', InventoryStatusFilter)
    prepopulated_fields = {
        'slug': ['title']
    }
    def clear_inventory(self, request: HttpRequest, queryset: QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products are successfully updated.',
            messages.ERROR
        )
    def discounted_price(self, obj): # obj represents each product object (row) in the admin page
        discount_percent = 10
        return obj.unit_price * (1 - discount_percent / 100)
    @admin.display(ordering='inventory')
    def inventory_status(self, obj):
        return 'Out of Stock' if obj.inventory == 0 else 'Low' if obj.inventory < 10 else 'Medium' if obj.inventory < 50 else 'OK'
    def collection_title(self, obj):
        # admin:app_model_page
        url = (
            reverse('admin:store_collection_changelist') 
                + '?'
                + urlencode(
                    {
                    'id': obj.collection_id
                    }
                )
        )
        return format_html('<a href="{}">{}</a>', url, obj.collection.title) if obj.collection else '-'

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'membership', 'orders', 'orders_count')
    list_editable = ('membership', )
    list_per_page = 50
    search_fields = ('first_name', 'last_name')
    ordering = ('first_name', 'last_name')
    search_fields = ('first_name__istartswith', 'last_name__istartswith') # this looks like in search box: .filter(fist_name__istartswith=search_query) OR .filter(last_name__istartswith=search_query)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (super()
                .get_queryset(request)
                .prefetch_related('order_set')
                .annotate(orders_count=Count('order'))
        )
    
    @admin.display(description='Orders')
    def orders(self, cust):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({
            'customer__id': cust.id
        })
        
        order_ids = cust.order_set.values_list('id', flat=True)
        return format_html('<a href="{}">{}</a>', url, ', '.join(str(order_id) for order_id in order_ids) or '-')
    
    def orders_count(self, cust):
        return cust.orders_count
    
class OrderItemInline(admin.StackedInline): # or StackedInline, # indirectly inherites from ModelAdmin
    autocomplete_fields = ['product']
    model=models.OrderItem
    min_num = 1
    max_num = 10
    extra = 0 # to remove place holers

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ('customer', )
    inlines = [OrderItemInline]
    list_display = ('id', 'place_at', 'payment_status', 'customer')
    list_per_page = 20
    # list_editable = ('payment_status', )
    list_select_related = ('customer', )

    def customer(self, order):
        return f'{order.customer.first_name} {order.customer.last_name}'

'''
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ('customer', )
    inlines = [OrderItemInline]
    list_display = ('id', 'place_at', 'payment_status', 'customer')
    list_per_page = 20
    # list_editable = ('payment_status', )
    list_select_related = ('customer', )

    def customer(self, order):
        return f'{order.customer.first_name} {order.customer.last_name}'
    
@admin.site.register(models.Order, OrderAdmin)
'''
