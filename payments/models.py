from django.db import models

from events.models import Events
from users.models import Users


class Payments(models.Model):
    timestamp = models.DateTimeField(null=False)
    price = models.DecimalField(null=False, decimal_places=2, max_digits=6)

    user = models.ForeignKey(Users, null=False, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'event',)

    def __str__(self):
        return f'User: {self.user} Event: {self.event}'
