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