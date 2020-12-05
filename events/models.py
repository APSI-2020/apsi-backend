from django.db import models


class Places(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)


class Events(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    limitOfParticipants = models.IntegerField()
    price = models.DecimalField()
    place = models.ForeignKey(Places, on_delete=models.CASCADE)


class Tickets(models.Model):
    qr_code_content = models.CharField(max_length=256)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
