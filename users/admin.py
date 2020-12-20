from django.contrib import admin

from .models import UsersTypes, UsersGroups, Users

admin.site.register(UsersTypes)
admin.site.register(UsersGroups)
admin.site.register(Users)
