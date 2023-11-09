# Register your models here.

from django.contrib import admin

from .models import EstateTransaction, EstateSubscription
from .models import Plan


class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'price', 'plan_type', 'status', 'timestamp')
    list_filter = ('status',)
    search_fields = ('plan_type',)
    ordering = ('-timestamp',)


admin.site.register(Plan, PlanAdmin)


@admin.register(EstateTransaction)
class EstateTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'estate_user', 'estate', 'plan', 'status', 'payment_type', 'timestamp')
    list_filter = ('status', 'payment_type', 'timestamp')
    search_fields = ('transaction_reference',)
    ordering = ('-timestamp',)


class EstateSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'estate', 'status', 'plan', 'payment_type', 'paid_date', 'due_date', 'timestamp')
    list_filter = ('status', 'plan', 'payment_type', 'paid_date', 'due_date')
    search_fields = ('estate__name', 'account_name', 'bank_name', 'account_number')
    ordering = ('-timestamp',)


admin.site.register(EstateSubscription, EstateSubscriptionAdmin)
