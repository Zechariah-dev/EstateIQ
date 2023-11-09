from django.contrib import admin

from estate_home_pages.models import WaitList


@admin.register(WaitList)
class EstateUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'timestamp')
    list_filter = ('id', 'email', 'timestamp')
    search_fields = ('id', 'email', 'timestamp')
    ordering = ('-timestamp',)
