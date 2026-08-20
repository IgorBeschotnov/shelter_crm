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

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Користувач")
    center = models.ForeignKey(
        Center, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Основний центр"
    )
    def __str__(self):
        return f"{self.user.username} — {self.center.name if self.center else 'Без центру'}"
class Room(models.Model):
    number = models.CharField(max_length=30, verbose_name="Номер/назва кімнати")
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="Центр")
    capacity = models.IntegerField(default=0, verbose_name="Місткість")

    def __str__(self):
        return f"{self.center.name} — {self.number}"

class Resident(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Чоловіча'
        FEMALE = 'F', 'Жіноча'

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