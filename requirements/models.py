from django.db import models

def empty_requirements():
    empty_requirements = Requirements(requirement_json='[]')
    empty_requirements.save()
    return empty_requirements.pk

class Requirements(models.Model):
    requirement_json = models.TextField()
