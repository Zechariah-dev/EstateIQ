from django.contrib import admin

from .models import EstateComplaint


@admin.register(EstateComplaint)
class EstateComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "estate",
        "title",
        "reason",
        "receivers",
        "status",
        "timestamp",
    )
    list_filter = ("estate", "status")
    search_fields = ("title", "reason")
