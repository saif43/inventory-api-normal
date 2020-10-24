from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext as _

# Register your models here.


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["username", "name"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal Info"), {"fields": ("name",)}),
        (
            _("Permissons"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_owner",
                    "is_manager",
                    "is_salesman",
                )
            },
        ),
        (_("Important_dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("username", "password1", "password2")},
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Shop)
admin.site.register(models.Warehouse)
admin.site.register(models.Product)
admin.site.register(models.Customer)
admin.site.register(models.Vendor)
admin.site.register(models.CustomerTrasnscation)
admin.site.register(models.CustomerOrderedItems)