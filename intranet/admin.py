"""
Настройка админ-панели для интранета DDC Biotech
Все модели зарегистрированы в одном файле
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

from .models import (
    User, Reagent, ReagentMovement, Recipe, RecipeReagent,
    Culture, CultureEvent, Task, TaskComment, Announcement,
    CalendarEvent, DocumentTemplate
)


# ============================================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админ-класс для кастомной модели пользователя
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'avatar_preview']
    list_display_links = ['username', 'email']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'avatar', 'profile_url')
        }),
    )
    
    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        """Превью аватара в списке"""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />',
                obj.avatar.url
            )
        return '—'


# ============================================================================
# РЕАГЕНТЫ
# ============================================================================

class ReagentMovementInline(admin.TabularInline):
    """
    Инлайн для отображения движений реагента
    """
    model = ReagentMovement
    extra = 1
    fields = ['movement_type', 'quantity', 'date', 'user', 'comment']
    raw_id_fields = ['user']
    readonly_fields = ['date']


@admin.register(Reagent)
class ReagentAdmin(admin.ModelAdmin):
    """
    Админ-класс для реагентов
    """
    list_display = [
        'name', 'category', 'on_hand_colored', 'min_threshold',
        'expiry_date_colored', 'image_preview', 'created_at'
    ]
    list_display_links = ['name']
    list_filter = ['category', 'created_at', 'expiry_date']
    search_fields = ['name', 'external_link']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'on_hand', 'min_threshold')
        }),
        ('Сроки и ссылки', {
            'fields': ('expiry_date', 'external_link')
        }),
        ('Файлы', {
            'fields': ('image', 'image_preview_large', 'certificate')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReagentMovementInline]
    
    actions = ['export_to_pdf', 'mark_as_critical']
    
    @admin.display(description='Остаток', ordering='on_hand')
    def on_hand_colored(self, obj):
        """Цветной вывод остатка"""
        if obj.on_hand <= obj.min_threshold:
            color = 'red'
        elif obj.on_hand <= obj.min_threshold * 1.5:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.on_hand
        )
    
    @admin.display(description='Срок годности', ordering='expiry_date')
    def expiry_date_colored(self, obj):
        """Цветной вывод срока годности"""
        if not obj.expiry_date:
            return '—'
        
        if obj.is_expiring_soon():
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.expiry_date.strftime('%d.%m.%Y')
            )
        return obj.expiry_date.strftime('%d.%m.%Y')
    
    @admin.display(description='Изображение')
    def image_preview(self, obj):
        """Маленькое превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return '—'
    
    @admin.display(description='Превью изображения')
    def image_preview_large(self, obj):
        """Большое превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.image.url
            )
        return 'Нет изображения'
    
    @admin.action(description='Экспорт в PDF')
    def export_to_pdf(self, request, queryset):
        """
        Генерация PDF с выбранными реагентами
        """
        # Создаём PDF в памяти
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Заголовок
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "DDC Biotech - Report Reagents")
        
        # Линия
        p.line(50, height - 60, width - 50, height - 60)
        
        # Данные
        y = height - 100
        p.setFont("Helvetica", 10)
        
        for reagent in queryset:
            if y < 50:  # Новая страница
                p.showPage()
                y = height - 50
                p.setFont("Helvetica", 10)
            
            text = f"{reagent.name} | Category: {reagent.get_category_display()} | Stock: {reagent.on_hand}"
            p.drawString(50, y, text)
            y -= 20
        
        p.showPage()
        p.save()
        
        # Возвращаем PDF
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reagents_report.pdf"'
        
        self.message_user(request, f'PDF создан для {queryset.count()} реагентов')
        return response
    
    @admin.action(description='Отметить как критические (для теста)')
    def mark_as_critical(self, request, queryset):
        """Массовое действие для тестирования"""
        count = queryset.update(on_hand=0)
        self.message_user(request, f'{count} реагентов отмечены как критические')


@admin.register(ReagentMovement)
class ReagentMovementAdmin(admin.ModelAdmin):
    """
    Админ-класс для движений реагентов
    """
    list_display = ['reagent', 'movement_type', 'quantity', 'date', 'user']
    list_filter = ['movement_type', 'date']
    search_fields = ['reagent__name', 'comment']
    date_hierarchy = 'date'
    raw_id_fields = ['reagent', 'user']


# ============================================================================
# РЕЦЕПТУРЫ
# ============================================================================

class RecipeReagentInline(admin.TabularInline):
    """
    Инлайн для реагентов в рецептуре
    """
    model = RecipeReagent
    extra = 2
    raw_id_fields = ['reagent']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-класс для рецептур
    """
    list_display = ['name', 'author', 'status', 'created_at', 'approved_at']
    list_display_links = ['name']
    list_filter = ['status', 'created_at', 'approved_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
    raw_id_fields = ['author']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = []  # reagents используют through, поэтому не используем filter_horizontal
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'author', 'status')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [RecipeReagentInline]
    
    actions = ['approve_recipes']
    
    @admin.action(description='Утвердить выбранные рецептуры')
    def approve_recipes(self, request, queryset):
        """
        Массовое утверждение рецептур
        """
        from django.utils import timezone
        count = queryset.update(status='approved', approved_at=timezone.now())
        self.message_user(request, f'{count} рецептур утверждено')


# ============================================================================
# КУЛЬТУРЫ
# ============================================================================

class CultureEventInline(admin.StackedInline):
    """
    Инлайн для событий культуры
    """
    model = CultureEvent
    extra = 1
    fields = ['event_type', 'date', 'user', 'comment']
    raw_id_fields = ['user']


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    """
    Админ-класс для культур
    """
    list_display = ['name', 'status', 'passage_number', 'seeding_date', 'responsible']
    list_display_links = ['name']
    list_filter = ['status', 'seeding_date']
    search_fields = ['name', 'notes']
    date_hierarchy = 'seeding_date'
    raw_id_fields = ['recipe', 'responsible']
    
    inlines = [CultureEventInline]


@admin.register(CultureEvent)
class CultureEventAdmin(admin.ModelAdmin):
    """
    Админ-класс для событий культуры
    """
    list_display = ['culture', 'event_type', 'date', 'user']
    list_filter = ['event_type', 'date']
    search_fields = ['culture__name', 'comment']
    date_hierarchy = 'date'
    raw_id_fields = ['culture', 'user']


# ============================================================================
# ЗАДАЧИ
# ============================================================================

class TaskCommentInline(admin.TabularInline):
    """
    Инлайн для комментариев к задаче
    """
    model = TaskComment
    extra = 1
    fields = ['user', 'text', 'date']
    readonly_fields = ['date']
    raw_id_fields = ['user']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Админ-класс для задач
    """
    list_display = [
        'title', 'assignee', 'creator', 'status_colored',
        'priority_colored', 'deadline', 'created_at'
    ]
    list_display_links = ['title']
    list_filter = ['status', 'priority', 'created_at', 'deadline']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    raw_id_fields = ['assignee', 'creator']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description')
        }),
        ('Участники и сроки', {
            'fields': ('assignee', 'creator', 'status', 'priority', 'deadline')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TaskCommentInline]
    
    @admin.display(description='Статус', ordering='status')
    def status_colored(self, obj):
        """Цветной статус"""
        colors = {
            'new': '#0d6efd',
            'in_progress': '#ffc107',
            'done': '#198754',
            'cancelled': '#6c757d',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'), obj.get_status_display()
        )
    
    @admin.display(description='Приоритет', ordering='priority')
    def priority_colored(self, obj):
        """Цветной приоритет"""
        colors = {
            'low': '#17a2b8',
            'normal': '#0d6efd',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#000'), obj.get_priority_display()
        )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """
    Админ-класс для комментариев к задачам
    """
    list_display = ['task', 'user', 'text_short', 'date']
    list_filter = ['date']
    search_fields = ['task__title', 'text']
    date_hierarchy = 'date'
    raw_id_fields = ['task', 'user']
    
    @admin.display(description='Текст')
    def text_short(self, obj):
        """Сокращённый текст"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


# ============================================================================
# ОБЪЯВЛЕНИЯ
# ============================================================================

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Админ-класс для объявлений
    """
    list_display = ['title', 'author', 'published_at', 'is_pinned_icon']
    list_display_links = ['title']
    list_filter = ['is_pinned', 'published_at']
    search_fields = ['title', 'text']
    date_hierarchy = 'published_at'
    raw_id_fields = ['author']
    
    @admin.display(description='Закреплено', boolean=True, ordering='is_pinned')
    def is_pinned_icon(self, obj):
        """Иконка для закреплённых"""
        return obj.is_pinned


# ============================================================================
# КАЛЕНДАРЬ
# ============================================================================

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """
    Админ-класс для событий календаря
    """
    list_display = ['subject', 'organizer', 'start_datetime', 'location']
    list_display_links = ['subject']
    list_filter = ['start_datetime']
    search_fields = ['subject', 'description', 'location']
    date_hierarchy = 'start_datetime'
    raw_id_fields = ['organizer']
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('subject', 'description', 'location')
        }),
        ('Участники и время', {
            'fields': ('organizer', 'participants', 'start_datetime', 'end_datetime')
        }),
    )


# ============================================================================
# ДОКУМЕНТЫ
# ============================================================================

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    """
    Админ-класс для документов
    """
    list_display = ['name', 'uploaded_by', 'uploaded_at', 'file_link']
    list_display_links = ['name']
    list_filter = ['uploaded_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'uploaded_at'
    raw_id_fields = ['uploaded_by']
    readonly_fields = ['uploaded_at']
    
    @admin.display(description='Файл')
    def file_link(self, obj):
        """Ссылка на файл"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">Скачать</a>',
                obj.file.url
            )
        return '—'


# Кастомизация админ-панели
admin.site.site_header = 'DDC Biotech Интранет'
admin.site.site_title = 'DDC Biotech Admin'
admin.site.index_title = 'Панель управления'
