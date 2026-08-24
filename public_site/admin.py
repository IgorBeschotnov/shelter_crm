from django.contrib import admin
from .models import Review, ConsultationRequest
from .models import Review, ConsultationRequest, NewsPost, TeamMember


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at')
    list_filter = ('is_published',)
    list_editable = ('is_published',)
    search_fields = ('title', 'text')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position_title', 'center', 'order')
    list_editable = ('order',)
    # list_editable не работает вместе с list_display_links по умолчанию на первом поле,
    # поэтому явно указываем, что кликабельная ссылка на редактирование — full_name
    list_display_links = ('full_name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # list_display — что видно в общем списке отзывов, без захода в каждый
    list_display = ('author_name', 'status', 'created_at')
    # list_filter — сбоку появится фильтр по статусу, чтобы быстро отделить
    # "На модерації" от уже обработанных
    list_filter = ('status',)
    # list_editable — статус можно менять прямо в списке, не заходя в отзыв
    list_editable = ('status',)
    # search_fields — поиск по имени автора и тексту отзыва
    search_fields = ('author_name', 'text')
    # readonly_fields — дата подачі не должна редактироваться руками
    readonly_fields = ('created_at',)


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'status', 'created_at')
    list_filter = ('status',)
    list_editable = ('status',)
    search_fields = ('name', 'contact')
    readonly_fields = ('created_at',)