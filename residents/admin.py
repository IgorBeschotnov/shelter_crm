from django.contrib import admin
from .models import Center, Room, Resident, Role, Position, PositionAssignment, ActionLog, RoleRequest

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

    fieldsets = (
        # Первый блок — кто это. Показывается первым, без подписи "Особисті дані"
        # можно оставить пустым заголовком (None), если хочешь, чтобы он шёл
        # без рамки-названия сверху — но с названием понятнее, оставляю с ним.
        ('Особисті дані', {
            'fields': ('full_name', 'sex', 'birth_date', 'phone', 'avatar'),
            # avatar тут же, рядом с ФИО — логично, это тоже "личные данные"
        }),

        ('Проживання', {
            'fields': ('room', 'bed_type', 'status', 'arrival_date', 'departure_date'),
            # room и bed_type — где живёт; status — presence (проживає/вибув);
            # даты прибытия/убытия тоже про физическое присутствие, поэтому здесь,
            # а не в "Особисті дані"
        }),

        ('Ролі та статус', {
            'fields': ('roles',),
            # Всего одно поле, но выносим в отдельный блок — потому что
            # filter_horizontal для M2M и так занимает много места на экране,
            # ему лучше своя секция, чем теряться среди коротких полей
        }),

        ('Додатково', {
            'fields': ('extra_attributes', 'notes'),
            'classes': ('collapse',),
            # 'collapse' — этот блок будет свёрнут по умолчанию при открытии формы.
            # Логично: extra_attributes (JSON под нестандартные случаи) и notes
            # нужны редко, не должны отвлекать при обычном редактировании
        }),
    )

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

@admin.register(RoleRequest)
class RoleRequestAdmin(admin.ModelAdmin):
    list_display = ('resident', 'current_role', 'target_role', 'initiated_by', 'status', 'created_at')
    list_filter = ('status', 'target_role', 'created_at')
    search_fields = ('resident__last_name', 'resident__first_name')