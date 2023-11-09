from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import EstateUser


@admin.register(EstateUser)
class EstateUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'estate', 'estate_zone', 'user', 'user_type', 'status', 'created_by', 'invited', 'timestamp')
    list_filter = ('estate', 'estate_zone', 'user', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    ordering = ('-timestamp',)
