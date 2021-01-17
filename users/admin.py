from django.contrib import admin

from .models import UsersGroups, Users

admin.site.register(UsersGroups)
admin.site.register(Users)
