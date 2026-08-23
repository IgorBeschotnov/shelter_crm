from django.contrib import admin
from .models import Center, Room, Resident, Role, Position, PositionAssignment, ActionLog

admin.site.register(Center)
admin.site.register(Room)
admin.site.register(Role)
admin.site.register(Position)
admin.site.register(PositionAssignment)
admin.site.register(ActionLog)


class ResidentAdmin(admin.ModelAdmin):
    filter_horizontal = ('roles',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            if not request.user.is_superuser:
                try:
                    # Центр беремо через кімнату самого залогіненого резидента
                    center = request.user.resident_profile.room.center
                    kwargs["queryset"] = Room.objects.filter(center=center)
                except (Resident.DoesNotExist, AttributeError):
                    # AttributeError — якщо в юзера немає resident_profile
                    # або в резидента ще не заповнена кімната
                    kwargs["queryset"] = Room.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Resident, ResidentAdmin)