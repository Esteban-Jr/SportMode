from django.contrib import admin
from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('email',)
    readonly_fields = ('email', 'date_subscribed')
    # Allow toggling is_active directly from the list view
    list_editable = ('is_active',)
    ordering = ('-date_subscribed',)
    actions = ['reactivate', 'deactivate']

    @admin.action(description='Reactivate selected subscribers')
    def reactivate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriber(s) reactivated.')

    @admin.action(description='Unsubscribe selected subscribers')
    def deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriber(s) unsubscribed.')
