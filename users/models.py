from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import UsersManager


class AcademicTitle(Enum):
    lic = "lic."
    inz = "inż."
    mgr = "mgr."
    dr = "dr."
    prof = "prof."
    prof_inz = "prof. inż."
    mgr_inz = "mgr inż."
    dr_inz = "dr inż."
    dr_hab = "dr hab."
    dr_hab_inz = "dr hab. inż."


class UsersTypes(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class UsersGroups(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Users(AbstractUser):
    username = None
    last_login = None
    date_joined = None

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(_('email address'), unique=True)

    title = models.CharField(max_length=32,
                             choices=[(tag.value, tag) for tag in AcademicTitle], null=True)
    groups = models.ManyToManyField(UsersGroups)
    types = models.ManyToManyField(UsersTypes)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
