from django.db import models

from requirements.models import Requirements
from users.models import Users


class Places(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)


class Events(models.Model):
    name = models.CharField(max_length=64)
    start = models.DateTimeField()
    end = models.DateTimeField()
    limit_of_participants = models.IntegerField()
    number_of_participants = models.IntegerField()
    price = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    place = models.ForeignKey(Places, on_delete=models.CASCADE)

    requirements = models.OneToOneField(Requirements, on_delete=models.CASCADE, null=True)
    lecturers = models.ManyToManyField(Users, related_name='hosted_events')
    participants = models.ManyToManyField(Users, related_name='events')


class Tickets(models.Model):
    qr_code_content = models.CharField(max_length=256)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
