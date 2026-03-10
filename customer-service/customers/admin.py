from django.contrib import admin
from .models import Address, Customer, FullName

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'display_name', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'fullname__full_name')
    ordering = ('-date_joined',)

    @admin.display(description='Name')
    def display_name(self, obj):
        return obj.name


@admin.register(FullName)
class FullNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name')
    search_fields = ('full_name',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'line1', 'city', 'state', 'country')
    search_fields = ('line1', 'city', 'state', 'country')
