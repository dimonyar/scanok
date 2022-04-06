import uuid

from crum import get_current_user

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField('email address', unique=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = str(uuid.uuid4())

        super().save(*args, **kwargs)


class Device(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=50)
    pseudonym = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        value = get_current_user().id
        self.user_id = value
        super(Device, self).save(*args, **kwargs)
