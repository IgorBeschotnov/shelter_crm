from django.contrib import admin
from .models import Center, Room, Resident, Role, Position, PositionAssignment, ActionLog

admin.site.register(Center)
admin.site.register(Role)
admin.site.register(Position)

class ResidentInline(admin.TabularInline):
    model = Resident
    fk_name = 'room'          # по якому полю Resident зв'язаний з Room
    extra = 0                 # не показувати порожні рядки для "додати нового"
    fields = ('full_name_display', 'birth_date', 'arrival_date', 'bed_type', 'roles_display', 'position_display')
    readonly_fields = ('full_name_display', 'roles_display', 'position_display')

    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = "ПІБ"

    def roles_display(self, obj):
        # M2M не можна показати прямо як поле в inline — збираємо текстом
        return ", ".join(r.name for r in obj.roles.all()) or "—"
    roles_display.short_description = "Ролі"

    def position_display(self, obj):
        # Активне призначення — те, де date_to ще не заповнена
        active = obj.positionassignment_set.filter(date_to__isnull=True).first()
        return active.position.name if active else "—"
    position_display.short_description = "Посада"


class RoomAdmin(admin.ModelAdmin):
    inlines = [ResidentInline]
    list_display = ('__str__', 'occupancy')

    def occupancy(self, obj):
        # Скільки верхніх/нижніх місць зайнято з наявних
        upper_taken = obj.resident_set.filter(bed_type='upper').count()
        lower_taken = obj.resident_set.filter(bed_type='lower').count()
        return f"Верх: {upper_taken}/{obj.beds_upper} · Низ: {lower_taken}/{obj.beds_lower}"
    occupancy.short_description = "Зайнятість"


admin.site.register(Room, RoomAdmin)

class ActionLogInline(admin.TabularInline):
    model = ActionLog
    extra = 1


class PositionAssignmentAdmin(admin.ModelAdmin):
    inlines = [ActionLogInline]


admin.site.register(PositionAssignment, PositionAssignmentAdmin)


class ResidentAdmin(admin.ModelAdmin):
    filter_horizontal = ('roles',)

    def _get_level(self, request):
        """Повертає рівень доступу поточного користувача (Position.Level) або None."""
        try:
            resident = request.user.resident_profile
            active = resident.positionassignment_set.filter(date_to__isnull=True).first()
            return active.position.level if active else None
        except AttributeError:
            return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            level = self._get_level(request)
            if not request.user.is_superuser and level != Position.Level.OWNER:
                try:
                    center = request.user.resident_profile.room.center
                    kwargs["queryset"] = Room.objects.filter(center=center)
                except (Resident.DoesNotExist, AttributeError):
                    kwargs["queryset"] = Room.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
admin.site.register(Resident, ResidentAdmin)