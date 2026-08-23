from django.contrib import admin
from .models import Center, Room, Resident, Role, Position, PositionAssignment, ActionLog

admin.site.register(Center)
admin.site.register(Room)
admin.site.register(Role)
admin.site.register(Position)


class ActionLogInline(admin.TabularInline):
    model = ActionLog
    extra = 1


class PositionAssignmentAdmin(admin.ModelAdmin):
    inlines = [ActionLogInline]


admin.site.register(PositionAssignment, PositionAssignmentAdmin)


class ResidentAdmin(admin.ModelAdmin):
    filter_horizontal = ('roles',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            if not request.user.is_superuser:
                try:
                    center = request.user.resident_profile.room.center
                    kwargs["queryset"] = Room.objects.filter(center=center)
                except (Resident.DoesNotExist, AttributeError):
                    kwargs["queryset"] = Room.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Resident, ResidentAdmin)