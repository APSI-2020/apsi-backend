from django.contrib import admin

from events.models import Places, Events, Tickets
from requirements.models import Requirements
from users.models import UsersTypes, UsersGroups, Users

admin.site.register(Places)
admin.site.register(Events)
admin.site.register(Tickets)
admin.site.register(Requirements)
admin.site.register(UsersTypes)
admin.site.register(UsersGroups)
admin.site.register(Users)
