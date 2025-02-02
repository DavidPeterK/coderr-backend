from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BusinessProfile, CustomerProfile


class BusinessProfileInline(admin.StackedInline):
    model = BusinessProfile
    can_delete = False
    verbose_name_plural = 'Business Profile'


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'type', 'is_staff')
    list_filter = ('type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
         'fields': ('first_name', 'last_name', 'email', 'type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'type'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.type == CustomUser.Types.BUSINESS:
                return [BusinessProfileInline]
            elif obj.type == CustomUser.Types.CUSTOMER:
                return [CustomerProfileInline]
        return []


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BusinessProfile)
admin.site.register(CustomerProfile)
