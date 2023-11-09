# Register your models here.
from django.contrib import admin

from estate_webhooks.models import Webhook


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('timestamp',)
    search_fields = ('timestamp',)
    ordering = ('-timestamp',)
