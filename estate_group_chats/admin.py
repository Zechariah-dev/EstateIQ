from django.contrib import admin
from .models import GroupMessage, GroupConversation

# Register your models here.

admin.site.register(GroupConversation)
admin.site.register(GroupMessage)
