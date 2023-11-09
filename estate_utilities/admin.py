# Register your models here.
from django.contrib import admin

from .models import EstateUtility, UtilityTransaction, EstateUtilityPenalty


class EstateUtilityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'estate', 'price', 'payment_frequency', 'timestamp']
    search_fields = ['name', 'estate__name', 'payment_frequency']
    list_filter = ['payment_frequency', 'timestamp']
    ordering = ['-timestamp']


admin.site.register(EstateUtility, EstateUtilityAdmin)


class UtilityTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'estate', 'estate_user', 'estate_utility', 'amount', 'payment_type', 'transaction_reference', 'status',
        'purpose', 'paid_date', 'due_date', 'timestamp')
    search_fields = (
        'id', 'estate__name', 'estate_user__user__email', 'estate_utility__name', 'transaction_reference', 'purpose')
    list_filter = ('status', 'payment_type', 'timestamp')


admin.site.register(UtilityTransaction, UtilityTransactionAdmin)


@admin.register(EstateUtilityPenalty)
class EstateUtilityPenaltyAdmin(admin.ModelAdmin):
    list_display = ('id', 'estate', 'estate_utility', 'unpaid_in', 'unpaid_period', 'revoke', 'timestamp')
    list_filter = ('estate', 'timestamp')
    search_fields = ('id', 'estate__name', 'estate_utility__name')
