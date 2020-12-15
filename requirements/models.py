from django.db import models
from django.db.utils import OperationalError


def empty_requirements():
    try:
        empty_requirements = Requirements(requirement_json='[]')
        empty_requirements.save()
        return empty_requirements
    except OperationalError:
        # happens when db doesn't exist yet
        pass

class Requirements(models.Model):
    requirement_json = models.TextField()
