from django.db import models
from enum import Enum


class UserType(Enum):
    STUDENT = "STUDENT"
    LECTURER = "LECTURER"
    GUEST = "GUEST"


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
    name = models.CharField(max_length=32,
                            choices=[(tag, tag.value) for tag in UserType])


class UsersGroups(models.Model):
    name = models.CharField(max_length=64)


class User(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    title = models.CharField(max_length=32,
                             choices=[(tag, tag.value) for tag in AcademicTitle], null=True)
    password_hash = models.CharField(max_length=64)
    groups = models.ManyToManyField(UsersGroups)
    types = models.ManyToManyField(UsersTypes)
