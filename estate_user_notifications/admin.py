# Register your models here.
from django.contrib import admin

from .models import EstateUserNotification, SuperAdminNotification


class EstateUserNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'estate_user', 'notification_type', 'read', 'timestamp')
    list_filter = ('read', 'notification_type', 'timestamp')
    search_fields = ('message', 'notification_type', "estate_user__estate__estate_id")
    ordering = ('-timestamp',)


admin.site.register(EstateUserNotification, EstateUserNotificationAdmin)
from django.contrib import admin


class SuperAdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification_type', 'redirect_url', 'read', 'timestamp')
    list_filter = ('notification_type', 'read', 'timestamp')
    search_fields = ('notification_type', 'message')


admin.site.register(SuperAdminNotification, SuperAdminNotificationAdmin)
