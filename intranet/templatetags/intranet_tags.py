"""
Пользовательские шаблонные теги и фильтры для интранета
"""

from django import template
from django.db.models import Count, Q
from django.utils import timezone
from intranet.models import Task, Announcement, Reagent

register = template.Library()


# ============================================================================
# ПРОСТОЙ ТЕГ - возвращает значение
# ============================================================================

@register.simple_tag
def count_pending_tasks(user=None):
    """
    Подсчитывает количество незавершенных задач
    Если передан пользователь, считает только его задачи
    """
    tasks = Task.objects.exclude(status='done')
    if user and user.is_authenticated:
        tasks = tasks.filter(assignee=user)
    return tasks.count()


@register.simple_tag
def count_announcements():
    """
    Подсчитывает общее количество объявлений
    """
    return Announcement.objects.count()


@register.simple_tag
def count_critical_reagents():
    """
    Подсчитывает количество критических реагентов
    """
    from django.db.models import F
    return Reagent.objects.filter(on_hand__lt=F('min_threshold')).count()


# ============================================================================
# ТЕГ С КОНТЕКСТОМ - использует контекст шаблона
# ============================================================================

@register.simple_tag(takes_context=True)
def active_menu_item(context, url_name):
    """
    Проверяет, активен ли пункт меню
    Используется для подсветки текущего раздела
    """
    request = context.get('request')
    if request:
        current_url = request.resolver_match.url_name if request.resolver_match else None
        return 'active' if current_url == url_name else ''
    return ''


@register.simple_tag(takes_context=True)
def user_greeting(context):
    """
    Возвращает приветствие для текущего пользователя
    """
    user = context.get('user')
    if user and user.is_authenticated:
        name = user.get_full_name() or user.username
        role_display = user.get_role_display() if hasattr(user, 'get_role_display') else ''
        
        # Определяем время суток для приветствия
        hour = timezone.now().hour
        if 5 <= hour < 12:
            greeting = 'Доброе утро'
        elif 12 <= hour < 18:
            greeting = 'Добрый день'
        elif 18 <= hour < 23:
            greeting = 'Добрый вечер'
        else:
            greeting = 'Доброй ночи'
        
        return f'{greeting}, {name}!'
    return 'Здравствуйте!'


# ============================================================================
# ТЕГ, ВОЗВРАЩАЮЩИЙ QUERYSET - inclusion tag
# ============================================================================

@register.inclusion_tag('widgets/pinned_announcements.html')
def show_pinned_announcements():
    """
    Возвращает закрепленные объявления для отображения
    """
    announcements = Announcement.objects.filter(
        is_pinned=True
    ).select_related('author').order_by('-published_at')[:3]
    
    return {
        'announcements': announcements,
    }


@register.inclusion_tag('widgets/recent_tasks.html', takes_context=True)
def show_recent_tasks(context, limit=5):
    """
    Показывает последние задачи текущего пользователя
    """
    user = context.get('user')
    tasks = Task.objects.none()
    
    if user and user.is_authenticated:
        tasks = Task.objects.filter(
            assignee=user
        ).exclude(
            status='done'
        ).select_related('creator').order_by('deadline')[:limit]
    
    return {
        'tasks': tasks,
        'user': user,
    }


@register.inclusion_tag('widgets/critical_reagents.html')
def show_critical_reagents(limit=5):
    """
    Показывает реагенты с критически низким остатком
    """
    from django.db.models import F
    
    reagents = Reagent.objects.filter(
        on_hand__lt=F('min_threshold')
    ).order_by('on_hand')[:limit]
    
    return {
        'reagents': reagents,
    }


# ============================================================================
# ASSIGNMENT TAG - сохраняет результат в переменную контекста
# ============================================================================

@register.simple_tag
def get_user_stats(user):
    """
    Возвращает статистику пользователя
    """
    if not user or not user.is_authenticated:
        return {}
    
    stats = {
        'total_tasks': Task.objects.filter(assignee=user).count(),
        'pending_tasks': Task.objects.filter(
            assignee=user, status='new'
        ).count(),
        'in_progress_tasks': Task.objects.filter(
            assignee=user, status='in_progress'
        ).count(),
        'completed_tasks': Task.objects.filter(
            assignee=user, status='done'
        ).count(),
    }
    
    return stats


@register.simple_tag
def get_latest_announcements(count=5):
    """
    Возвращает последние объявления
    """
    return Announcement.objects.select_related('author').order_by(
        '-is_pinned', '-published_at'
    )[:count]


# ============================================================================
# FILTER TAG - фильтр для использования в шаблонах
# ============================================================================

@register.filter(name='pluralize_ru')
def pluralize_ru(value, endings='а,ов,ов'):
    """
    Русская плюрализация
    Пример: {{ count|pluralize_ru:"задача,задачи,задач" }}
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return ''
    
    endings_list = endings.split(',')
    if len(endings_list) != 3:
        return ''
    
    if value % 10 == 1 and value % 100 != 11:
        return endings_list[0]
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        return endings_list[1]
    else:
        return endings_list[2]


@register.filter(name='status_badge')
def status_badge(status):
    """
    Возвращает CSS-класс Bootstrap badge для статуса
    """
    status_classes = {
        'new': 'bg-primary',
        'in_progress': 'bg-warning',
        'done': 'bg-success',
        'cancelled': 'bg-secondary',
        'active': 'bg-success',
        'frozen': 'bg-info',
        'discarded': 'bg-danger',
        'draft': 'bg-secondary',
        'approved': 'bg-success',
        'archived': 'bg-dark',
    }
    return status_classes.get(status, 'bg-secondary')


@register.filter(name='priority_badge')
def priority_badge(priority):
    """
    Возвращает CSS-класс Bootstrap badge для приоритета
    """
    priority_classes = {
        'low': 'bg-info',
        'normal': 'bg-primary',
        'high': 'bg-warning',
        'urgent': 'bg-danger',
    }
    return priority_classes.get(priority, 'bg-secondary')


@register.filter(name='days_until')
def days_until(date):
    """
    Возвращает количество дней до указанной даты
    """
    if not date:
        return None
    
    from datetime import date as date_type, datetime
    
    if isinstance(date, datetime):
        date = date.date()
    
    today = timezone.now().date()
    delta = date - today
    
    return delta.days


@register.filter(name='format_file_size')
def format_file_size(bytes_size):
    """
    Форматирует размер файла в человекочитаемый вид
    """
    try:
        bytes_size = float(bytes_size)
    except (ValueError, TypeError):
        return '0 Б'
    
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} ТБ"


