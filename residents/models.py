from django.db import models
from django.contrib.auth.models import User

class Center(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва центру")
    director = models.CharField(max_length=100, blank=True, verbose_name="Директор")

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name="Назва ролі")

    def __str__(self):
        return self.name

class Room(models.Model):
    number = models.CharField(max_length=30, verbose_name="Номер/назва кімнати")
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="Центр")
    capacity = models.IntegerField(default=0, verbose_name="Місткість")
    beds_upper = models.PositiveIntegerField(default=0, verbose_name="Верхніх місць")
    beds_lower = models.PositiveIntegerField(default=0, verbose_name="Нижніх місць")
    notes = models.TextField(null=True, blank=True, verbose_name="Примітки (інвентар тощо)")

    def __str__(self):
        return f"{self.center.name} — {self.number}"


class Resident(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Чоловіча'
        FEMALE = 'F', 'Жіноча'

    class BedType(models.TextChoices):
        UPPER = 'upper', 'Верхнє'
        LOWER = 'lower', 'Нижнє'

    bed_type = models.CharField(
        max_length=10, choices=BedType.choices, null=True, blank=True,
        verbose_name="Місце"
    )

    class Status(models.TextChoices):
        RESIDING = 'residing', 'Проживає'
        DEPARTED = 'departed', 'Вибув'
        HOSPITALIZED = 'hospitalized', 'У лікарні'
        TEMPORARY_ABSENT = 'absent', 'Тимчасово відсутній'

    last_name = models.CharField(max_length=50, verbose_name="Прізвище")
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    middle_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="По батькові"
    )
    gender = models.CharField(
        max_length=1, choices=Gender.choices, verbose_name="Стать"
    )
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Дата народження"
    )

    room = models.ForeignKey(
        'Room', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Кімната"
    )

        # Обліковий запис для входу в кабінет — не у всіх резидентів він є
    user_account = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resident_profile', verbose_name="Обліковий запис"
    )

    roles = models.ManyToManyField(Role, blank=True, verbose_name="Ролі")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RESIDING,
        verbose_name="Статус",
    )
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Телефон"
    )

    arrival_date = models.DateField(
        null=True, blank=True, verbose_name="Дата прибуття"
    )
    departure_date = models.DateField(
        null=True, blank=True, verbose_name="Дата вибуття"
    )

    notes = models.TextField(null=True, blank=True, verbose_name="Примітки")
    extra_attributes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Додаткові атрибути",
        help_text="Довільні дані (захворювання, суди, пільги тощо)",
    )

    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True, verbose_name="Фото"
        )
    
    class Meta:
        verbose_name = "Підопічний"
        verbose_name_plural = "Підопічні"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        date_str = (
            self.birth_date.strftime('%d.%m.%Y')
            if self.birth_date
            else 'дата народження не вказана'
        )
        return f"{self.full_name} ({date_str})"

    @property
    def full_name(self):
        """Повертає повне ПІБ з урахуванням відсутнього по батькові."""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)

    @property
    def short_name(self):
        """Повертає ім'я у форматі: Прізвище І. Б."""
        init_i = f" {self.first_name[0]}." if self.first_name else ""
        init_o = f" {self.middle_name[0]}." if self.middle_name else ""
        return f"{self.last_name}{init_i}{init_o}"

class Position(models.Model):
    """Посада — фіксований список рівнів доступу, тому Level всередині."""
    class Level(models.TextChoices):
        OWNER = 'owner', 'Власник'
        BRANCH_DIRECTOR = 'branch_director', 'Директор філії'
        CENTER_DIRECTOR = 'center_director', 'Директор центру'
        ADMIN_1 = 'admin_1', 'Адміністратор 1'
        ADMIN_2 = 'admin_2', 'Адміністратор 2'
        ADMIN_3 = 'admin_3', 'Адміністратор 3'

    name = models.CharField(max_length=100, verbose_name="Назва посади")
    level = models.CharField(max_length=20, choices=Level.choices, verbose_name="Рівень доступу")

    def __str__(self):
        return self.name


class PositionAssignment(models.Model):
    """Період, коли конкретний резидент займав конкретну посаду.
    date_to = None означає, що призначення досі активне."""
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, verbose_name="Резидент")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Посада")
    date_from = models.DateField(verbose_name="Дата призначення")
    date_to = models.DateField(null=True, blank=True, verbose_name="Дата завершення")

    def __str__(self):
        period = f"{self.date_from} — {self.date_to or 'дотепер'}"
        return f"{self.resident} на посаді «{self.position}» ({period})"


class ActionLog(models.Model):
    """Розпорядження/дії в рамках конкретного призначення на посаду."""
    assignment = models.ForeignKey(
        PositionAssignment, on_delete=models.CASCADE,
        related_name='actions', verbose_name="Призначення"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата дії")
    description = models.TextField(verbose_name="Опис дії")

    def __str__(self):
        return f"{self.date:%d.%m.%Y} — {self.description[:50]}"


class RoleRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На рассмотрении'
        APPROVED = 'approved', 'Утверждено'
        REJECTED = 'rejected', 'Отклонено'

    # Кто предлагает (например, старший комнаты)
    initiated_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='initiated_role_requests',
        verbose_name='Хто запропонував'
    )
    
    # Кому предлагают (житель)
    resident = models.ForeignKey(
        Resident, 
        on_delete=models.CASCADE, 
        related_name='role_requests',
        verbose_name='Підопічний'
    )
    
    # Текущая роль (чтобы было видно "С КАКОЙ РОЛИ")
    current_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='from_role_requests',
        verbose_name='Поточна роль'
    )

    # Запрашиваемая роль (из списка ролей, созданного администратором — "НА КАКУЮ РОЛЬ")
    target_role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='to_role_requests',
        verbose_name='Цільова роль'
    )
    
    # Статус заявки
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        verbose_name='Статус'
    )
    
    # Кто реально утвердил (администратор / ответственный)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_role_requests',
        verbose_name='Хто затвердив'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        verbose_name = "Заявка на зміну ролі"
        verbose_name_plural = "Заявки на зміну ролей"

    def __str__(self):
        from_role = self.current_role.name if self.current_role else "Без ролі"
        return f"Заявка: {self.resident.short_name} ({from_role} ➔ {self.target_role.name}) — {self.get_status_display()}"