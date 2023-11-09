from django.contrib import admin

from estate_access_logs.models import EstateAccessLog


class EstateAccessLogAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'from_date', 'to_date', 'access', 'timestamp')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('access',)


admin.site.register(EstateAccessLog, EstateAccessLogAdmin)
