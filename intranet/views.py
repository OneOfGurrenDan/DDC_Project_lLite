"""
Представления (Views) для интранета DDC Biotech
Все view-функции собраны в одном файле (FBV - Function-Based Views)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, F, Avg, Sum
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from datetime import timedelta

from .models import (
    User, Reagent, ReagentMovement, Recipe, RecipeReagent,
    Culture, CultureEvent, Task, TaskComment, Announcement,
    CalendarEvent, DocumentTemplate
)
from .forms import (
    UserLoginForm, UserRegisterForm, ReagentForm, ReagentMovementForm,
    RecipeForm, CultureForm, TaskForm, TaskCommentForm,
    AnnouncementForm, SearchForm, DocumentTemplateForm
)


# ============================================================================
# ГЛАВНАЯ СТРАНИЦА (ДАШБОРД) - ЗАДАНИЕ 15
# ============================================================================

@login_required
@cache_page(60 * 5)  # Кеш на 5 минут
def dashboard(request):
    """
    Главная страница с виджетами и поиском
    
    Демонстрирует:
    - Виджеты с данными из 3+ таблиц
    - aggregate(), Count(), F()
    - Поиск с __icontains, __contains, values(), values_list(), count(), exists()
    - Пагинацию с try/except
    """
    
    # Обработка поиска
    search_query = request.GET.get('q', '')
    search_results = []
    
    if search_query:
        # Поиск реагентов
        reagents = Reagent.objects.filter(
            Q(name__icontains=search_query) | 
            Q(category__contains=search_query)
        ).values('id', 'name', 'category')[:5]
        
        # Поиск задач
        tasks = Task.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        ).values_list('id', 'title', 'status')[:5]
        
        # Поиск объявлений
        announcements_found = Announcement.objects.filter(
            Q(title__icontains=search_query) |
            Q(text__icontains=search_query)
        )
        
        search_results = {
            'reagents': list(reagents),
            'tasks': list(tasks),
            'announcements_count': announcements_found.count(),
            'announcements_exist': announcements_found.exists(),
        }
        
        # Сохраняем последний поиск в сессию
        request.session['last_search'] = search_query
    
    # ВИДЖЕТ 1: Последние объявления
    latest_announcements = Announcement.objects.select_related('author').order_by(
        '-is_pinned', '-published_at'
    )[:5]
    
    # ВИДЖЕТ 2: Актуальные задачи текущего пользователя
    user_tasks = Task.objects.filter(
        assignee=request.user
    ).exclude(
        status='done'
    ).select_related('creator').order_by('deadline', '-priority')[:5]
    
    # Подсчет просроченных задач
    overdue_tasks_count = Task.objects.filter(
        assignee=request.user,
        deadline__lt=timezone.now()
    ).exclude(status='done').count()
    
    # ВИДЖЕТ 3: Критические реагенты
    # Реагенты с остатком ниже минимального порога
    critical_reagents = Reagent.objects.filter(
        on_hand__lt=F('min_threshold')
    ).order_by('on_hand')[:5]
    
    # Реагенты с истекающим сроком годности (следующие 30 дней)
    expiring_soon = Reagent.objects.filter(
        expiry_date__lte=timezone.now().date() + timedelta(days=30),
        expiry_date__gte=timezone.now().date()
    ).order_by('expiry_date')[:5]
    
    # СТАТИСТИКА с агрегацией
    stats = {
        'total_reagents': Reagent.objects.count(),
        'total_tasks': Task.objects.filter(assignee=request.user).count(),
        'active_cultures': Culture.objects.filter(status='active').count(),
        'pending_tasks': Task.objects.filter(
            assignee=request.user,
            status='new'
        ).count(),
    }
    
    # Агрегация: общее количество движений по типам
    movements_stats = ReagentMovement.objects.values('movement_type').annotate(
        total=Count('id')
    )
    
    # Пагинация для списка всех объявлений (если нужно)
    all_announcements = Announcement.objects.all().order_by('-published_at')
    paginator = Paginator(all_announcements, 10)
    page = request.GET.get('page', 1)
    
    try:
        announcements_page = paginator.page(page)
    except PageNotAnInteger:
        announcements_page = paginator.page(1)
    except EmptyPage:
        announcements_page = paginator.page(paginator.num_pages)
    
    context = {
        'latest_announcements': latest_announcements,
        'user_tasks': user_tasks,
        'overdue_tasks_count': overdue_tasks_count,
        'critical_reagents': critical_reagents,
        'expiring_soon': expiring_soon,
        'stats': stats,
        'movements_stats': movements_stats,
        'search_query': search_query,
        'search_results': search_results,
        'announcements_page': announcements_page,
    }
    
    return render(request, 'dashboard.html', context)


# ============================================================================
# CRUD ОБЪЕКТОВ (РЕАГЕНТЫ) - ЗАДАНИЕ 16
# ============================================================================

@login_required
def object_list(request):
    """
    Список реагентов с фильтрацией
    
    Демонстрирует:
    - filter(), exclude(), order_by()
    - chaining QuerySet
    - срезы [:10]
    """
    reagents_list = Reagent.objects.all()
    
    # Фильтрация
    category = request.GET.get('category')
    if category:
        reagents_list = reagents_list.filter(category=category)
    
    # Фильтр критических реагентов
    if request.GET.get('critical') == 'true':
        reagents_list = reagents_list.filter(on_hand__lt=F('min_threshold'))
    
    # Сортировка
    sort_by = request.GET.get('sort', 'name')
    reagents_list = reagents_list.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(reagents_list, 15)
    page = request.GET.get('page')
    reagents = paginator.get_page(page)
    
    # Категории для фильтра
    categories = Reagent.CATEGORY_CHOICES
    
    context = {
        'reagents': reagents,
        'categories': categories,
        'selected_category': category,
    }
    
    return render(request, 'object_list.html', context)


@login_required
def object_detail(request, pk):
    """
    Детальная страница реагента
    
    Демонстрирует:
    - get_object_or_404()
    - select_related(), prefetch_related()
    """
    # Получаем реагент с предзагрузкой связанных данных
    reagent = get_object_or_404(
        Reagent.objects.prefetch_related('movements__user'),
        pk=pk
    )
    
    # Получаем последние движения
    recent_movements = reagent.movements.all()[:10]
    
    # Рецепты, использующие этот реагент
    recipes = reagent.used_in_recipes.all().select_related('author')
    
    # Проверка прав доступа (пример)
    user_role = request.user.role
    can_edit = user_role in ['lab_head', 'sysadmin']
    can_delete = user_role == 'sysadmin'
    
    context = {
        'object': reagent,
        'recent_movements': recent_movements,
        'recipes': recipes,
        'can_edit': can_edit,
        'can_delete': can_delete,
    }
    
    return render(request, 'object_detail.html', context)


@login_required
def object_create(request):
    """
    Создание нового реагента
    
    Демонстрирует:
    - ModelForm
    - is_valid()
    - cleaned_data
    - обработка request.FILES
    """
    # Проверка прав
    if request.user.role not in ['lab_head', 'sysadmin']:
        raise Http404("У вас нет прав для создания реагентов")
    
    if request.method == 'POST':
        form = ReagentForm(request.POST, request.FILES)
        if form.is_valid():
            reagent = form.save()
            messages.success(request, f'Реагент "{reagent.name}" успешно создан')
            return HttpResponseRedirect(reagent.get_absolute_url())
    else:
        form = ReagentForm()
    
    context = {
        'form': form,
        'title': 'Создать реагент',
    }
    
    return render(request, 'forms/object_form.html', context)


@login_required
def object_update(request, pk):
    """
    Редактирование реагента
    
    Демонстрирует:
    - save(commit=True)
    - частичное редактирование полей
    """
    reagent = get_object_or_404(Reagent, pk=pk)
    
    # Проверка прав
    if request.user.role not in ['lab_head', 'sysadmin']:
        messages.error(request, 'У вас нет прав для редактирования реагентов')
        return redirect('reagent_detail', pk=pk)
    
    if request.method == 'POST':
        form = ReagentForm(request.POST, request.FILES, instance=reagent)
        if form.is_valid():
            updated_reagent = form.save(commit=True)
            messages.success(request, f'Реагент "{updated_reagent.name}" обновлен')
            return HttpResponseRedirect(updated_reagent.get_absolute_url())
    else:
        form = ReagentForm(instance=reagent)
    
    context = {
        'form': form,
        'title': f'Редактировать: {reagent.name}',
        'object': reagent,
    }
    
    return render(request, 'forms/object_form.html', context)


@login_required
def object_delete(request, pk):
    """
    Удаление реагента
    
    Демонстрирует:
    - delete()
    - HttpResponseRedirect
    """
    reagent = get_object_or_404(Reagent, pk=pk)
    
    # Проверка прав
    if request.user.role != 'sysadmin':
        raise Http404("Только системный администратор может удалять реагенты")
    
    if request.method == 'POST':
        reagent_name = reagent.name
        reagent.delete()
        messages.success(request, f'Реагент "{reagent_name}" удален')
        return HttpResponseRedirect(reverse('object_list'))
    
    context = {
        'object': reagent,
    }
    
    return render(request, 'object_confirm_delete.html', context)


# ============================================================================
# ДРУГИЕ СПИСКИ И ФИЛЬТРАЦИЯ
# ============================================================================

@login_required
def task_list(request):
    """
    Список задач с фильтрацией
    
    Демонстрирует:
    - Цепочку фильтров (chaining)
    - update() на QuerySet
    """
    tasks = Task.objects.all().select_related('assignee', 'creator')
    
    # Фильтры
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)
    
    # Только мои задачи
    if request.GET.get('my_tasks') == 'true':
        tasks = tasks.filter(assignee=request.user)
    
    # Исключаем выполненные
    if request.GET.get('hide_done') == 'true':
        tasks = tasks.exclude(status='done')
    
    # Сортировка
    tasks = tasks.order_by('deadline', '-priority')
    
    # Массовое обновление (если передан параметр)
    if request.method == 'POST' and 'mark_done' in request.POST:
        task_ids = request.POST.getlist('task_ids')
        Task.objects.filter(id__in=task_ids).update(status='done')
        messages.success(request, f'Отмечено выполненными: {len(task_ids)} задач')
        return redirect('task_list')
    
    paginator = Paginator(tasks, 20)
    page = request.GET.get('page')
    tasks_page = paginator.get_page(page)
    
    context = {
        'tasks': tasks_page,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    
    return render(request, 'task_list.html', context)


@login_required
def reagent_list_filtered(request):
    """
    Расширенная фильтрация реагентов
    
    Демонстрирует:
    - values() и values_list()
    - различные lookup'ы
    """
    # Получаем уникальные категории через values_list
    categories = Reagent.objects.values_list('category', flat=True).distinct()
    
    # Выборка с values() - только нужные поля
    reagents_data = Reagent.objects.values(
        'id', 'name', 'category', 'on_hand', 'min_threshold'
    ).filter(on_hand__gt=0).order_by('name')[:50]
    
    context = {
        'categories': categories,
        'reagents_data': reagents_data,
    }
    
    return render(request, 'reagent_list_filtered.html', context)


# ============================================================================
# АУТЕНТИФИКАЦИЯ И СЕССИИ
# ============================================================================

def login_view(request):
    """
    Вход в систему
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Сохраняем время входа в сессию
                request.session['login_time'] = timezone.now().isoformat()
                
                messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
                
                # Перенаправление на следующую страницу или дашборд
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'auth/login.html', context)


def logout_view(request):
    """
    Выход из системы
    """
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')


def register_view(request):
    """
    Регистрация нового пользователя
    
    Демонстрирует работу с сессиями
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Автоматический вход после регистрации
            login(request, user)
            
            # Сохраняем в сессию информацию о регистрации
            request.session['is_new_user'] = True
            request.session['registration_date'] = timezone.now().isoformat()
            
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'auth/register.html', context)


# ============================================================================
# РАБОТА С ФАЙЛАМИ И ЗАГРУЗКАМИ
# ============================================================================

@login_required
def upload_document(request):
    """
    Загрузка документа
    
    Демонстрирует:
    - Обработку request.FILES
    """
    if request.method == 'POST':
        form = DocumentTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Документ успешно загружен')
            return redirect('document_list')
    else:
        form = DocumentTemplateForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'forms/document_form.html', context)


@login_required
def document_list(request):
    """
    Список документов
    """
    documents = DocumentTemplate.objects.all().select_related('uploaded_by').order_by('-uploaded_at')
    
    paginator = Paginator(documents, 20)
    page = request.GET.get('page')
    documents_page = paginator.get_page(page)
    
    context = {
        'documents': documents_page,
    }
    
    return render(request, 'document_list.html', context)


# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ VIEW
# ============================================================================

@login_required
def culture_list(request):
    """
    Список культур
    """
    cultures = Culture.objects.all().select_related(
        'responsible', 'recipe'
    ).prefetch_related('events')
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        cultures = cultures.filter(status=status)
    
    cultures = cultures.order_by('-seeding_date')
    
    paginator = Paginator(cultures, 15)
    page = request.GET.get('page')
    cultures_page = paginator.get_page(page)
    
    context = {
        'cultures': cultures_page,
        'status_choices': Culture.STATUS_CHOICES,
    }
    
    return render(request, 'culture_list.html', context)


@login_required
def recipe_list(request):
    """
    Список рецептур
    """
    recipes = Recipe.objects.all().select_related('author').prefetch_related('reagents')
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        recipes = recipes.filter(status=status)
    
    recipes = recipes.order_by('-created_at')
    
    paginator = Paginator(recipes, 15)
    page = request.GET.get('page')
    recipes_page = paginator.get_page(page)
    
    context = {
        'recipes': recipes_page,
        'status_choices': Recipe.STATUS_CHOICES,
    }
    
    return render(request, 'recipe_list.html', context)


@login_required
def announcement_list(request):
    """
    Список всех объявлений
    """
    announcements = Announcement.objects.all().select_related('author').order_by(
        '-is_pinned', '-published_at'
    )
    
    paginator = Paginator(announcements, 20)
    page = request.GET.get('page')
    announcements_page = paginator.get_page(page)
    
    context = {
        'announcements': announcements_page,
    }
    
    return render(request, 'announcement_list.html', context)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ VIEW
# ============================================================================

def custom_404(request, exception):
    """
    Кастомная страница 404
    """
    return render(request, '404.html', status=404)


def custom_500(request):
    """
    Кастомная страница 500
    """
    return render(request, '500.html', status=500)
