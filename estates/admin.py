from django.contrib import admin

# Register your models here.
from django.contrib import admin

from estates.models import Estate


class EstateAdmin(admin.ModelAdmin):
    list_display = ('id', 'estate_id', 'name', 'country', 'state', 'lga', 'status', 'timestamp')
    list_filter = ('status', 'country', 'state', 'lga')
    search_fields = ('estate_id', 'name', 'country', 'address', 'state', 'lga')
    ordering = ('-timestamp',)


admin.site.register(Estate, EstateAdmin)
