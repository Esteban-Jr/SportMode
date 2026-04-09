from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'friendly_name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'sport', 'price',
        'stock_quantity', 'is_active', 'is_featured',
    )
    list_filter = ('is_active', 'is_featured', 'sport', 'category')
    list_editable = ('price', 'stock_quantity', 'is_active', 'is_featured')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Identity', {
            'fields': ('name', 'slug', 'sku', 'category', 'sport'),
        }),
        ('Description', {
            'fields': ('short_description', 'description'),
        }),
        ('Pricing', {
            'fields': ('price', 'original_price'),
        }),
        ('Media', {
            'fields': ('image', 'image_url'),
        }),
        ('Inventory & Visibility', {
            'fields': ('stock_quantity', 'is_active', 'is_featured'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
