from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OfficialSignature


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Permissions', {'fields': ('role', 'can_view_history', 'can_print_certificates', 'can_edit_records', 'can_delete_records', 'is_active_user')}),
    )
    list_display = ('username', 'get_full_name', 'role', 'is_active', 'date_created')
    list_filter = ('role', 'is_active', 'date_created')


@admin.register(OfficialSignature)
class OfficialSignatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'date_created')
    list_filter = ('is_active', 'position', 'date_created')
    search_fields = ('name', 'position')
    readonly_fields = ('date_created', 'date_updated')
