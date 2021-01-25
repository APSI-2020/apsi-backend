from django.db import models

from requirements.models import Requirements
from users.models import Users


class Places(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Events(models.Model):
    name = models.CharField(max_length=64)
    start = models.DateTimeField()
    end = models.DateTimeField()
    limit_of_participants = models.IntegerField()
    number_of_participants = models.IntegerField(default=0)
    price = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    root = models.ForeignKey('Events', on_delete=models.CASCADE, null=True, blank=True)
    is_root = models.BooleanField(default=False, null=False)

    requirements = models.OneToOneField(Requirements, on_delete=models.CASCADE, null=False)
    lecturers = models.ManyToManyField(Users, related_name='hosted_events')
    participants = models.ManyToManyField(Users, related_name='events')

    def __str__(self):
        return self.name

    def is_participant(self, user):
        return self.participants.filter(pk=user.pk).exists()
