from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemInline,)

    readonly_fields = (
        'order_number', 'date', 'user_profile',
        'delivery_cost', 'order_total', 'grand_total',
        'original_bag', 'stripe_pid',
    )
    fields = (
        'order_number', 'user_profile', 'date',
        'full_name', 'email', 'phone_number',
        'street_address1', 'street_address2',
        'town_or_city', 'county', 'postcode', 'country',
        'delivery_cost', 'order_total', 'grand_total',
        'original_bag', 'stripe_pid',
    )
    list_display = (
        'order_number', 'date', 'full_name',
        'order_total', 'delivery_cost', 'grand_total',
    )
    ordering = ('-date',)
    search_fields = ('order_number', 'full_name', 'email', 'stripe_pid')
