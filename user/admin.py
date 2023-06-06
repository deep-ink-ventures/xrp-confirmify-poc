from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(OriginalUserAdmin):
    ordering = ["id"]

    readonly_fields = ["last_login", "date_joined"]

    list_display = [
        "email", "first_name", "last_name", 'date_joined', 'is_active', 'is_staff', 'is_superuser'
    ]

    fieldsets = OriginalUserAdmin.fieldsets + (
        ("Profile", {"fields": (
            "wallet_address",
        )}),
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
    )
