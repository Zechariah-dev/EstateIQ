from django.contrib import admin

# Register your models here.
from django.contrib import admin

from estate_adverts.models import EstateAdvertisement, EstateReminder, EstateAnnouncement


class EstateAdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'timestamp')
    search_fields = ('title', 'description')


class EstateAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'announcement_date', 'recipients', 'timestamp')
    search_fields = ('title', 'description')


class EstateReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'reminder_date', 'recipients', 'timestamp')
    search_fields = ('title', 'description')


admin.site.register(EstateAdvertisement, EstateAdvertisementAdmin)
admin.site.register(EstateAnnouncement, EstateAnnouncementAdmin)
admin.site.register(EstateReminder, EstateReminderAdmin)
