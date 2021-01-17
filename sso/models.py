from django.db import models

from users.models import Users


class SignedUsers(models.Model):
    sso_id = models.UUIDField()
    access_token = models.CharField(max_length=32)
    user = models.ForeignKey(Users, on_delete=models.PROTECT, null=False, default=0)
