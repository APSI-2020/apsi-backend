from django.contrib import admin

from .models import Places, Events, Tickets

admin.site.register(Places)
admin.site.register(Events)
admin.site.register(Tickets)
