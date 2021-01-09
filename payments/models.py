from django.db import models
from users.models import Users
from events.models import Events

class Payments(models.Model):
   date = models.DateTimeField()
   price = models.DecimalField(null=True, decimal_places=2, max_digits=6)

   user = models.ForeignKey(Users, on_delete=models.CASCADE)
   event = models.ForeignKey(Events, on_delete=models.CASCADE)

   def __str__(self):
       return f'User: {self.user} Event: {self.event}'
