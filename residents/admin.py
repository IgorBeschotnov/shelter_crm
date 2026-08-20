from django.contrib import admin
from .models import Center, Room, Resident, Role

# Register your models here.
admin.site.register(Center)
admin.site.register(Room)
admin.site.register(Role)
admin.site.register(Resident)

