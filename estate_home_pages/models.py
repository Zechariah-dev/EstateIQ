from django.db import models


# Create your models here.

class WaitList(models.Model):
    email = models.EmailField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
