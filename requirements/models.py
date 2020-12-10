from django.db import models


class Requirements(models.Model):
    requirement_json = models.TextField()
