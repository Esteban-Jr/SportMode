from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Embeds the UserProfile form directly inside the User admin page.
    This means staff can view and edit a user's delivery defaults
    without navigating to a separate admin record.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Unregister the default User admin and re-register with the inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Standalone UserProfile admin for direct access — useful for
    searching or bulk-reviewing profiles separately from Users.
    """
    list_display = ('user', 'default_full_name', 'default_town_or_city', 'default_country')
    search_fields = ('user__username', 'user__email', 'default_full_name')
    readonly_fields = ('user',)
