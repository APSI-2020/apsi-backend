from django.db import models


class Requirements(models.Model):
    requirementJson = models.TextField()
