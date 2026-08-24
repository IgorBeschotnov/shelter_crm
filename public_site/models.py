from django.db import models

class Review(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING = 'pending', 'На модерації'
        PUBLISHED = 'published', 'Опубліковано'
        REJECTED = 'rejected', 'Відхилено'

    author_name = models.CharField(max_length=100, verbose_name="Ім'я автора")
    text = models.TextField(verbose_name="Текст відгуку")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подання")
    status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        verbose_name="Статус модерації",
    )

    def __str__(self):
        return f"{self.author_name} ({self.get_status_display()})"


class ConsultationRequest(models.Model):
    class RequestStatus(models.TextChoices):
        NEW = 'new', 'Нова'
        IN_PROGRESS = 'in_progress', 'В обробці'
        DONE = 'done', 'Оброблена'

    name = models.CharField(max_length=100, verbose_name="Ім'я")
    contact = models.CharField(max_length=100, verbose_name="Телефон/контакт")
    comment = models.TextField(blank=True, verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.NEW,
        verbose_name="Статус",
    )

    def __str__(self):
        return f"{self.name} — {self.get_status_display()}"
    
class NewsPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    # photo/video через посилання (по ТЗ), не файловая загрузка —
    # значит просто текстовые поля-ссылки, а не ImageField/FileField
    photo_url = models.URLField(blank=True, verbose_name="Посилання на фото")
    video_url = models.URLField(blank=True, verbose_name="Посилання на відео")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публікації")
    # is_published — щоб можна було готувати чернетку і публікувати пізніше,
    # не через created_at (коли написано), а явним флагом
    is_published = models.BooleanField(default=False, verbose_name="Опубліковано")

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="ПІБ")
    position_title = models.CharField(max_length=150, verbose_name="Посада/роль")
    bio = models.TextField(blank=True, verbose_name="Біографія")
    photo_url = models.URLField(blank=True, verbose_name="Посилання на фото")
    # center — якщо картка прив'язана до конкретного центру (лідерський склад
    # центру), а не загальна для всієї мережі
    center = models.ForeignKey(
        'residents.Center', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Центр"
    )
    # order — щоб самому визначати порядок показу на сайті (директор перший тощо),
    # а не покладатися на алфавіт чи дату створення
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок показу")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.full_name}"