from django.contrib import admin
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'created_at')
    filter_horizontal = ('products',)
