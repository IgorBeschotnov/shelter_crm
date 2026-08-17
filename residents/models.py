from django.db import models
class Center(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название центра")
    director = models.CharField(max_length=100, blank=True, verbose_name="Директор")

    def __str__(self):
        return self.name
class Room(models.Model):
    number = models.CharField(max_length=30, verbose_name="Номер/название комнаты")
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="Центр")
    capacity = models.IntegerField(default=0, verbose_name="Вместимость")

    def __str__(self):
        return f"{self.center.name} — {self.number}"

class Resident(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Мужской'
        FEMALE = 'F', 'Женский'

    class Status(models.TextChoices):
        RESIDING = 'residing', 'Проживает'
        DEPARTED = 'departed', 'Убыл'
        HOSPITALIZED = 'hospitalized', 'В больнице'
        TEMPORARY_ABSENT = 'absent', 'Временно отсутствует'

    # Основные данные
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Отчество"
    )
    gender = models.CharField(
        max_length=1, choices=Gender.choices, verbose_name="Пол"
    )
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Дата рождения"
    )

    # Размещение и статус
    room = models.ForeignKey(
    'Room', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Комната"
)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RESIDING,
        verbose_name="Статус",
    )
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Телефон"
    )

    # Даты пребывания
    arrival_date = models.DateField(
        null=True, blank=True, verbose_name="Дата прибытия"
    )
    departure_date = models.DateField(
        null=True, blank=True, verbose_name="Дата убытия"
    )

    # Заметки и доп. поля
    notes = models.TextField(null=True, blank=True, verbose_name="Примечания")
    extra_attributes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Доп. атрибуты",
        help_text="Произвольные данные (заболевания, суды, льготы и т.д.)",
    )

    class Meta:
        verbose_name = "Подопечный"
        verbose_name_plural = "Подопечные"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        date_str = (
            self.birth_date.strftime('%d.%m.%Y')
            if self.birth_date
            else 'дата рождения не указана'
        )
        return f"{self.full_name} ({date_str})"

    @property
    def full_name(self):
        """Возвращает полное ФИО с учетом отсутствующего отчества."""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)

    @property
    def short_name(self):
        """Возвращает имя в формате: Фамилия И. О."""
        init_i = f" {self.first_name[0]}." if self.first_name else ""
        init_o = f" {self.middle_name[0]}." if self.middle_name else ""
        return f"{self.last_name}{init_i}{init_o}"