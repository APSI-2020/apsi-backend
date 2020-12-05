from django.db import models

from requirements.models import Requirements


class Places(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)


class Events(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    limitOfParticipants = models.IntegerField()
    price = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    requirements = models.OneToOneField(Requirements, on_delete=models.CASCADE, null=True)


class Tickets(models.Model):
    qr_code_content = models.CharField(max_length=256)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
