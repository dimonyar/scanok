import uuid

from crum import get_current_user

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.templatetags.static import static


def upload_avatar(instance, filename: str) -> str:
    return f'{instance.id}/avatars/{filename}'


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField('email address', unique=True)
    avatar = models.FileField(upload_to=upload_avatar, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = str(uuid.uuid4())

        super().save(*args, **kwargs)

    def avatar_url(self):
        if self.avatar:
            return self.avatar.url

        return static('img/avatar-anon.png')


class Device(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=50)
    pseudonym = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    current = models.BooleanField(default=False)

    @transaction.atomic
    def save(self, *args, **kwargs):

        if self.current:
            Device.objects.filter(current=True, user_id=get_current_user().id).update(current=False)
        else:
            if not Device.objects.filter(current=True, user_id=get_current_user().id).exclude(id=self.id):
                self.current = True
        value = get_current_user().id
        self.user_id = value
        super(Device, self).save(*args, **kwargs)
