import uuid

from django.db import models

# Create your models here.
from estate_users.models import EstateUser


class GroupConversation(models.Model):
    """
    this is used as a group conversation between
     the admin to the  residents and externals
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # this would be the id of the conversation
    # so right now i would be using the estate_resident_estate_id for the name
    name = models.CharField(max_length=300)
    # If true this means that conversation was created by the superuser
    is_super_user = models.BooleanField(default=False)
    online = models.ManyToManyField(to=EstateUser, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def get_online_count(self):
        # shows the number of online users in this conversation
        return self.online.count()

    def join(self, user):
        # add a user to the online user
        self.online.add(user)
        self.save()

    def leave(self, user):
        #  remove the user once he is not connected
        self.online.remove(user)
        self.save()


class GroupMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_conversation = models.ForeignKey(
        GroupConversation, on_delete=models.CASCADE, related_name="group_mesages"
    )
    from_user = models.ForeignKey(
        EstateUser, on_delete=models.CASCADE, blank=True, null=True
    )
    # If true this means the message was created by the super user
    is_super_user = models.BooleanField(default=False)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f"From {self.from_user.id}: {self.content} [{self.timestamp}]"
