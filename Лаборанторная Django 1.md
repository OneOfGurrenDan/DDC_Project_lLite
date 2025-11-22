# Лабораторная Django 1 - Защита

## Содержание
1. [Метод __str__ в модели](#метод-__str__-в-модели)
2. [Использование from django.utils import timezone](#использование-from-djangoutils-import-timezone)
3. [class Meta: ordering](#class-meta-ordering)
4. [choices в поле модели](#choices-в-поле-модели)
5. [related_name в модели](#related_name-в-модели)
6. [Метод filter() в view](#метод-filter-в-view)
7. [Использование __ (два подчеркивания)](#использование-__-два-подчеркивания)
8. [Метод exclude()](#метод-exclude)
9. [Метод order_by()](#метод-order_by)
10. [Использование собственного модельного менеджера](#использование-собственного-модельного-менеджера)
11. [get_object_or_404()](#get_object_or_404)
12. [Использование 2х шаблонных фильтров](#использование-2х-шаблонных-фильтров)
13. [get_absolute_url, reverse](#get_absolute_url-reverse)
14. [Пагинация (+ try, except)](#пагинация--try-except)
15. [Функция агрегирования](#функция-агрегирования)
16. [Создание простого шаблонного тега](#создание-простого-шаблонного-тега)
17. [Создание шаблонного тега с контекстными переменными](#создание-шаблонного-тега-с-контекстными-переменными)
18. [Создание шаблонного тега, возвращающего набор запросов](#создание-шаблонного-тега-возвращающего-набор-запросов)
19. [Аутентификация и регистрация пользователя](#аутентификация-и-регистрация-пользователя)

---

## Метод __str__ в модели

### Что это?
Метод `__str__()` определяет строковое представление объекта модели. Это то, что вы увидите в Django Admin, shell и при выводе объекта.

### Назначение:
- Читаемое представление объекта
- Отображение в админке Django
- Удобная отладка
- Использование в логах

### Примеры в проекте:

**Пример 1: Модель User**
```50:51:intranet/models.py
def __str__(self):
    return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
```
*Использует `get_full_name()` и `get_role_display()` для отображения имени и роли пользователя.*

**Пример 2: Модель Reagent**
```131:132:intranet/models.py
def __str__(self):
    return f"{self.name} ({self.get_category_display()})"
```
*Показывает название реагента и его категорию в читаемом виде.*

**Пример 3: Модель ReagentMovement**
```191:192:intranet/models.py
def __str__(self):
    return f"{self.get_movement_type_display()}: {self.reagent.name} - {self.quantity}"
```
*Отображает тип движения, название реагента и количество.*

**Пример 4: Модель Task**
```467:468:intranet/models.py
def __str__(self):
    return f"{self.title} ({self.get_status_display()})"
```

**Пример 5: Модель Culture**
```358:359:intranet/models.py
def __str__(self):
    return f"{self.name} (P{self.passage_number})"
```
*Использует номер пассажа для биологических культур.*

---

## Использование from django.utils import timezone

### Что это?
Модуль `timezone` предоставляет timezone-aware функции для работы с датами и временем.

### Назначение:
- Корректная работа с часовыми поясами
- Получение текущего времени с учетом настроек проекта
- Сравнение дат с учетом timezone

### Примеры в проекте:

**Пример 1: Импорт в models.py**
```9:9:intranet/models.py
from django.utils import timezone
```

**Пример 2: Использование timezone.now() как default**
```176:176:intranet/models.py
date = models.DateTimeField('Дата', default=timezone.now)
```
*Используется для автоматической установки текущей даты при создании записи.*

**Пример 3: Проверка истекающего срока годности**
```142:147:intranet/models.py
def is_expiring_soon(self):
    """Проверяет, истекает ли срок годности в ближайшие 30 дней"""
    if not self.expiry_date:
        return False
    days_left = (self.expiry_date - timezone.now().date()).days
    return 0 <= days_left <= 30
```

**Пример 4: В view для фильтрации просроченных задач**
```94:97:intranet/views.py
overdue_tasks_count = Task.objects.filter(
    assignee=request.user,
    deadline__lt=timezone.now()
).exclude(status='done').count()
```

**Пример 5: В шаблонном теге для определения времени суток**
```74:74:intranet/templatetags/intranet_tags.py
hour = timezone.now().hour
```

**Пример 6: Сохранение времени входа в сессию**
```434:434:intranet/views.py
request.session['login_time'] = timezone.now().isoformat()
```

---

## class Meta: ordering

### Что это?
Атрибут `ordering` в классе `Meta` определяет порядок сортировки объектов по умолчанию.

### Назначение:
- Автоматическая сортировка QuerySet'ов
- Избежание повторения order_by() в запросах
- Определение логики сортировки на уровне модели

### Примеры в проекте:

**Пример 1: User - сортировка по username**
```45:48:intranet/models.py
class Meta:
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'
    ordering = ['username']
```

**Пример 2: Reagent - сортировка по названию**
```126:129:intranet/models.py
class Meta:
    verbose_name = 'Реагент'
    verbose_name_plural = 'Реагенты'
    ordering = ['name']
```

**Пример 3: ReagentMovement - сортировка по убыванию даты**
```186:189:intranet/models.py
class Meta:
    verbose_name = 'Движение реагента'
    verbose_name_plural = 'Движения реагентов'
    ordering = ['-date']
```
*Знак минус `-` означает сортировку по убыванию (от новых к старым).*

**Пример 4: Recipe - сортировка по дате создания (новые первыми)**
```255:258:intranet/models.py
class Meta:
    verbose_name = 'Рецептура'
    verbose_name_plural = 'Рецептуры'
    ordering = ['-created_at']
```

**Пример 5: Task - сортировка по нескольким полям**
```462:465:intranet/models.py
class Meta:
    verbose_name = 'Задача'
    verbose_name_plural = 'Задачи'
    ordering = ['deadline', '-priority']
```
*Сначала по дедлайну (возрастание), затем по приоритету (убывание).*

**Пример 6: Announcement - составная сортировка**
```529:532:intranet/models.py
class Meta:
    verbose_name = 'Объявление'
    verbose_name_plural = 'Объявления'
    ordering = ['-is_pinned', '-published_at']
```
*Закрепленные объявления сначала, затем по дате публикации.*

---

## choices в поле модели

### Что это?
Атрибут `choices` ограничивает значения поля предопределенным набором вариантов.

### Назначение:
- Валидация данных на уровне БД
- Создание выпадающих списков в формах
- Получение человекочитаемых значений через `get_FOO_display()`
- Предотвращение ошибок ввода

### Примеры в проекте:

**Пример 1: Роли пользователей**
```21:31:intranet/models.py
ROLE_CHOICES = [
    ('employee', 'Сотрудник'),
    ('lab_head', 'Заведующий лабораторией'),
    ('sysadmin', 'Системный администратор'),
]

role = models.CharField(
    'Роль',
    max_length=20,
    choices=ROLE_CHOICES,
    default='employee'
)
```

**Пример 2: Категории реагентов**
```70:84:intranet/models.py
CATEGORY_CHOICES = [
    ('buffer', 'Буфер'),
    ('enzyme', 'Фермент'),
    ('antibody', 'Антитело'),
    ('chemical', 'Химическое вещество'),
    ('media', 'Среда'),
    ('other', 'Прочее'),
]

name = models.CharField('Название', max_length=255)
category = models.CharField(
    'Категория',
    max_length=20,
    choices=CATEGORY_CHOICES
)
```

**Пример 3: Типы движения реагентов**
```155:175:intranet/models.py
MOVEMENT_CHOICES = [
    ('in', 'Приход'),
    ('out', 'Расход'),
]

reagent = models.ForeignKey(
    Reagent,
    on_delete=models.CASCADE,
    related_name='movements',
    verbose_name='Реагент'
)
quantity = models.DecimalField(
    'Количество',
    max_digits=10,
    decimal_places=2
)
movement_type = models.CharField(
    'Тип движения',
    max_length=10,
    choices=MOVEMENT_CHOICES
)
```

**Пример 4: Статусы задач**
```416:450:intranet/models.py
STATUS_CHOICES = [
    ('new', 'Новая'),
    ('in_progress', 'В работе'),
    ('done', 'Выполнена'),
    ('cancelled', 'Отменена'),
]

PRIORITY_CHOICES = [
    ('low', 'Низкий'),
    ('normal', 'Обычный'),
    ('high', 'Высокий'),
    ('urgent', 'Срочный'),
]

title = models.CharField('Заголовок', max_length=255)
description = models.TextField('Описание')
assignee = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='assigned_tasks',
    verbose_name='Исполнитель'
)
creator = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='created_tasks',
    verbose_name='Создатель'
)
status = models.CharField(
    'Статус',
    max_length=20,
    choices=STATUS_CHOICES,
    default='new'
)
```

**Пример 5: Единицы измерения (через промежуточную модель)**
```271:298:intranet/models.py
UNIT_CHOICES = [
    ('ml', 'мл'),
    ('g', 'г'),
    ('mg', 'мг'),
    ('ul', 'мкл'),
    ('units', 'ед.'),
]

recipe = models.ForeignKey(
    Recipe,
    on_delete=models.CASCADE,
    verbose_name='Рецептура'
)
reagent = models.ForeignKey(
    Reagent,
    on_delete=models.CASCADE,
    verbose_name='Реагент'
)
quantity = models.DecimalField(
    'Количество',
    max_digits=10,
    decimal_places=2
)
unit = models.CharField(
    'Единица измерения',
    max_length=10,
    choices=UNIT_CHOICES,
    default='ml'
)
```

---

## related_name в модели

### Что это?
Атрибут `related_name` определяет имя обратной связи от связанной модели.

### Назначение:
- Доступ к связанным объектам с понятным именем
- Избежание конфликтов имен
- Улучшение читаемости кода
- Оптимизация запросов с prefetch_related()

### Примеры в проекте:

**Пример 1: Движения реагентов**
```160:164:intranet/models.py
reagent = models.ForeignKey(
    Reagent,
    on_delete=models.CASCADE,
    related_name='movements',
    verbose_name='Реагент'
)
```
*Теперь можно получить все движения реагента: `reagent.movements.all()`*

**Пример 2: Множественные связи в User**
```178:184:intranet/models.py
user = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='reagent_movements',
    verbose_name='Пользователь'
)
```
*Доступ: `user.reagent_movements.all()` - все движения реагентов этого пользователя.*

**Пример 3: Рецептуры и реагенты (ManyToMany)**
```245:249:intranet/models.py
reagents = models.ManyToManyField(
    Reagent,
    through='RecipeReagent',
    related_name='used_in_recipes',
    verbose_name='Реагенты'
)
```
*Доступ: `reagent.used_in_recipes.all()` - все рецептуры, где используется реагент.*

**Пример 4: Автор рецептур**
```232:237:intranet/models.py
author = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='recipes',
    verbose_name='Автор'
)
```

**Пример 5: Множественные связи Task с User**
```432:437:intranet/models.py
assignee = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='assigned_tasks',
    verbose_name='Исполнитель'
)
```

```439:444:intranet/models.py
creator = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='created_tasks',
    verbose_name='Создатель'
)
```
*Два разных related_name для разных ролей пользователя в задаче!*

**Пример 6: События культуры**
```378:382:intranet/models.py
culture = models.ForeignKey(
    Culture,
    on_delete=models.CASCADE,
    related_name='events',
    verbose_name='Культура'
)
```

---

## Метод filter() в view

### Что это?
Метод `filter()` возвращает QuerySet с объектами, соответствующими заданным условиям.

### Назначение:
- Фильтрация данных из БД
- Построение сложных запросов
- Цепочки фильтров (chaining)
- Оптимизация запросов

### Примеры в проекте:

**Пример 1: Базовая фильтрация по полю**
```87:88:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
)
```

**Пример 2: Цепочка фильтров**
```87:91:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
).exclude(
    status='done'
).select_related('creator').order_by('deadline', '-priority')[:5]
```

**Пример 3: Фильтрация с использованием F-выражений**
```101:103:intranet/views.py
critical_reagents = Reagent.objects.filter(
    on_hand__lt=F('min_threshold')
).order_by('on_hand')[:5]
```

**Пример 4: Фильтрация по диапазону дат**
```106:109:intranet/views.py
expiring_soon = Reagent.objects.filter(
    expiry_date__lte=timezone.now().date() + timedelta(days=30),
    expiry_date__gte=timezone.now().date()
).order_by('expiry_date')[:5]
```

**Пример 5: Множественные условия**
```94:97:intranet/views.py
overdue_tasks_count = Task.objects.filter(
    assignee=request.user,
    deadline__lt=timezone.now()
).exclude(status='done').count()
```

**Пример 6: Фильтрация с Q-объектами (OR)**
```54:57:intranet/views.py
reagents = Reagent.objects.filter(
    Q(name__icontains=search_query) | 
    Q(category__contains=search_query)
).values('id', 'name', 'category')[:5]
```

**Пример 7: Условная фильтрация из GET-параметров**
```171:174:intranet/views.py
category = request.GET.get('category')
if category:
    reagents_list = reagents_list.filter(category=category)
```

---

## Использование __ (два подчеркивания)

### Что это?
Двойное подчеркивание `__` используется для:
1. **Lookup'ов** - операций сравнения в фильтрах
2. **Обращения к полям связанных таблиц** (через ForeignKey)

### Назначение:
- Доступ к полям через связи
- Специальные операции фильтрации
- Построение сложных запросов

### Вариант 1: Lookup методы

**Пример 1: `__icontains` - регистронезависимый поиск**
```54:56:intranet/views.py
reagents = Reagent.objects.filter(
    Q(name__icontains=search_query) | 
    Q(category__contains=search_query)
```

**Пример 2: `__lt` - меньше чем (less than)**
```94:96:intranet/views.py
overdue_tasks_count = Task.objects.filter(
    assignee=request.user,
    deadline__lt=timezone.now()
```

**Пример 3: `__lte` и `__gte` - меньше/больше или равно**
```106:108:intranet/views.py
expiring_soon = Reagent.objects.filter(
    expiry_date__lte=timezone.now().date() + timedelta(days=30),
    expiry_date__gte=timezone.now().date()
```

**Пример 4: `__gt` - больше чем (greater than)**
```62:63:intranet/models.py
def get_queryset(self):
    return super().get_queryset().filter(on_hand__gt=0)
```

**Пример 5: `__in` - вхождение в список**
```369:370:intranet/views.py
task_ids = request.POST.getlist('task_ids')
Task.objects.filter(id__in=task_ids).update(status='done')
```

### Вариант 2: Обращение к связанным таблицам

**Пример 1: Доступ к полю автора через ForeignKey**
```82:84:intranet/views.py
latest_announcements = Announcement.objects.select_related('author').order_by(
    '-is_pinned', '-published_at'
)[:5]
```
*В шаблоне: `{{ announcement.author.username }}` или в запросе: `author__username`*

**Пример 2: Фильтрация по полю связанной модели**
```60:63:intranet/views.py
tasks = Task.objects.filter(
    Q(title__icontains=search_query) |
    Q(description__icontains=search_query)
).values_list('id', 'title', 'status')[:5]
```

**Пример 3: Prefetch через связи**
```211:213:intranet/views.py
reagent = get_object_or_404(
    Reagent.objects.prefetch_related('movements__user'),
    pk=pk
)
```
*Загружает реагент -> его движения -> пользователей каждого движения.*

**Пример 4: Select related через несколько уровней**
```345:345:intranet/views.py
tasks = Task.objects.all().select_related('assignee', 'creator')
```

**Пример 5: В поиске по связанным полям**
```397:397:intranet/views.py
categories = Reagent.objects.values_list('category', flat=True).distinct()
```

---

## Метод exclude()

### Что это?
Метод `exclude()` возвращает QuerySet, исключающий объекты, соответствующие заданным условиям (противоположность `filter()`).

### Назначение:
- Исключение нежелательных записей
- Построение "отрицательных" запросов
- Комбинация с filter() для сложной логики

### Примеры в проекте:

**Пример 1: Исключение выполненных задач**
```87:91:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
).exclude(
    status='done'
).select_related('creator').order_by('deadline', '-priority')[:5]
```

**Пример 2: Подсчет просроченных (но не выполненных) задач**
```94:97:intranet/views.py
overdue_tasks_count = Task.objects.filter(
    assignee=request.user,
    deadline__lt=timezone.now()
).exclude(status='done').count()
```

**Пример 3: Условное исключение**
```360:362:intranet/views.py
if request.GET.get('hide_done') == 'true':
    tasks = tasks.exclude(status='done')
```

**Пример 4: В шаблонном теге**
```115:118:intranet/templatetags/intranet_tags.py
tasks = Task.objects.filter(
    assignee=user
).exclude(
    status='done'
```

**Пример 5: В простом теге**
```23:23:intranet/templatetags/intranet_tags.py
tasks = Task.objects.exclude(status='done')
```

---

## Метод order_by()

### Что это?
Метод `order_by()` сортирует QuerySet по заданным полям.

### Назначение:
- Динамическая сортировка запросов
- Переопределение сортировки из Meta.ordering
- Множественная сортировка по полям

### Примеры в проекте:

**Пример 1: Сортировка по одному полю**
```181:182:intranet/views.py
sort_by = request.GET.get('sort', 'name')
reagents_list = reagents_list.order_by(sort_by)
```

**Пример 2: Сортировка по убыванию (знак минус)**
```82:84:intranet/views.py
latest_announcements = Announcement.objects.select_related('author').order_by(
    '-is_pinned', '-published_at'
)[:5]
```

**Пример 3: Множественная сортировка**
```87:91:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
).exclude(
    status='done'
).select_related('creator').order_by('deadline', '-priority')[:5]
```
*Сначала по deadline (возрастание), затем по priority (убывание).*

**Пример 4: Сортировка критических реагентов**
```101:103:intranet/views.py
critical_reagents = Reagent.objects.filter(
    on_hand__lt=F('min_threshold')
).order_by('on_hand')[:5]
```

**Пример 5: Сортировка по дате**
```106:109:intranet/views.py
expiring_soon = Reagent.objects.filter(
    expiry_date__lte=timezone.now().date() + timedelta(days=30),
    expiry_date__gte=timezone.now().date()
).order_by('expiry_date')[:5]
```

**Пример 6: В списке задач**
```365:365:intranet/views.py
tasks = tasks.order_by('deadline', '-priority')
```

---

## Использование собственного модельного менеджера

### Что это?
Кастомный менеджер (Manager) - это класс, расширяющий `models.Manager` для добавления специальных QuerySet методов.

### Назначение:
- Инкапсуляция сложной логики запросов
- Повторное использование запросов
- Разделение логики выборки данных
- Удобный API для работы с моделью

### Примеры в проекте:

**Пример 1: Определение кастомного менеджера**
```58:63:intranet/models.py
class ActiveReagentManager(models.Manager):
    """
    Кастомный менеджер для активных реагентов (с остатком больше 0)
    """
    def get_queryset(self):
        return super().get_queryset().filter(on_hand__gt=0)
```

**Пример 2: Добавление менеджеров к модели**
```122:124:intranet/models.py
# Менеджеры
objects = models.Manager()
active = ActiveReagentManager()
```
*Оба менеджера доступны! `objects` - стандартный, `active` - кастомный.*

**Использование:**

```python
# Все реагенты (стандартный менеджер)
all_reagents = Reagent.objects.all()

# Только реагенты с остатком > 0 (кастомный менеджер)
active_reagents = Reagent.active.all()

# Можно комбинировать с другими методами
expensive_active = Reagent.active.filter(price__gt=1000).order_by('-price')
```

**Зачем два менеджера?**
- `objects` - для полного доступа ко всем записям
- `active` - для быстрой фильтрации активных реагентов

**Альтернативный пример (можно добавить):**

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='approved')

class Recipe(models.Model):
    # ... поля ...
    objects = models.Manager()
    published = PublishedManager()  # Recipe.published.all() - только утвержденные
```

---

## get_object_or_404()

### Что это?
Функция `get_object_or_404()` пытается получить объект из БД, а при отсутствии возвращает HTTP 404.

### Назначение:
- Безопасное получение объекта
- Автоматическая обработка ошибок
- Улучшение UX (правильные коды ответов)
- Упрощение кода view

### Примеры в проекте:

**Пример 1: Импорт функции**
```6:6:intranet/views.py
from django.shortcuts import render, redirect, get_object_or_404
```

**Пример 2: Получение реагента с prefetch**
```211:213:intranet/views.py
reagent = get_object_or_404(
    Reagent.objects.prefetch_related('movements__user'),
    pk=pk
)
```
*Если реагента с таким pk нет - вернется 404.*

**Пример 3: Простое получение объекта**
```279:279:intranet/views.py
reagent = get_object_or_404(Reagent, pk=pk)
```

**Пример 4: В функции удаления**
```313:313:intranet/views.py
reagent = get_object_or_404(Reagent, pk=pk)
```

**Сравнение с обычным подходом:**

```python
# БЕЗ get_object_or_404 (плохо)
try:
    reagent = Reagent.objects.get(pk=pk)
except Reagent.DoesNotExist:
    raise Http404("Реагент не найден")

# С get_object_or_404 (хорошо)
reagent = get_object_or_404(Reagent, pk=pk)
```

**Дополнительные возможности:**

```python
# С несколькими условиями
task = get_object_or_404(Task, pk=task_id, assignee=request.user)

# С QuerySet
active_task = get_object_or_404(Task.objects.filter(status='active'), pk=task_id)

# Для списка объектов
from django.shortcuts import get_list_or_404
reagents = get_list_or_404(Reagent, category='enzyme')
```

---

## Использование 2х шаблонных фильтров

### Что это?
Шаблонные фильтры - это функции для преобразования данных непосредственно в шаблонах Django.

### Назначение:
- Форматирование данных в шаблонах
- Избежание логики в шаблонах
- Повторное использование преобразований
- Улучшение читаемости шаблонов

### Примеры в проекте:

**Пример 1: Фильтр для русской плюрализации**
```185:205:intranet/templatetags/intranet_tags.py
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
```

**Использование в шаблоне:**
```django
{{ task_count }} {{ task_count|pluralize_ru:"задача,задачи,задач" }}
```

**Пример 2: Фильтр для CSS-класса статуса**
```208:225:intranet/templatetags/intranet_tags.py
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
```

**Использование:**
```django
<span class="badge {{ task.status|status_badge }}">{{ task.get_status_display }}</span>
```

**Пример 3: Фильтр для бейджа приоритета**
```228:239:intranet/templatetags/intranet_tags.py
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
```

**Пример 4: Фильтр для подсчета дней до даты**
```242:258:intranet/templatetags/intranet_tags.py
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
```

**Пример 5: Фильтр для форматирования размера файла**
```261:276:intranet/templatetags/intranet_tags.py
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
```

---

## get_absolute_url, reverse

### Что это?
- `get_absolute_url()` - метод модели, возвращающий канонический URL объекта
- `reverse()` - функция для получения URL по имени маршрута

### Назначение:
- DRY принцип (Don't Repeat Yourself)
- Централизованное управление URL
- Избежание хардкода путей
- Автоматическое построение ссылок

### Примеры в проекте:

**Пример 1: Импорт в models.py**
```8:8:intranet/models.py
from django.urls import reverse
```

**Пример 2: get_absolute_url в модели Reagent**
```134:136:intranet/models.py
def get_absolute_url(self):
    """Возвращает URL для детальной страницы реагента"""
    return reverse('reagent_detail', kwargs={'pk': self.pk})
```

**Пример 3: get_absolute_url в модели Recipe**
```263:264:intranet/models.py
def get_absolute_url(self):
    return reverse('recipe_detail', kwargs={'pk': self.pk})
```

**Пример 4: get_absolute_url в модели Culture**
```361:362:intranet/models.py
def get_absolute_url(self):
    return reverse('culture_detail', kwargs={'pk': self.pk})
```

**Пример 5: get_absolute_url в модели Task**
```470:471:intranet/models.py
def get_absolute_url(self):
    return reverse('task_detail', kwargs={'pk': self.pk})
```

**Пример 6: Использование reverse в view**
```258:258:intranet/views.py
return HttpResponseRedirect(reagent.get_absolute_url())
```

**Пример 7: Reverse с именем маршрута**
```323:323:intranet/views.py
return HttpResponseRedirect(reverse('object_list'))
```

**Пример 8: Импорт reverse в views**
```11:11:intranet/views.py
from django.urls import reverse
```

**Использование в шаблонах:**

```django
{# Использование get_absolute_url #}
<a href="{{ reagent.get_absolute_url }}">{{ reagent.name }}</a>

{# Использование url template tag (аналог reverse) #}
<a href="{% url 'reagent_detail' pk=reagent.pk %}">{{ reagent.name }}</a>

{# С параметрами #}
<a href="{% url 'task_list' %}?status=new">Новые задачи</a>
```

**Определение маршрутов:**
```23:28:intranet/urls.py
# CRUD ОБЪЕКТОВ (РЕАГЕНТЫ) - Задание 16
# ========================================
path('objects/', views.object_list, name='object_list'),
path('objects/<int:pk>/', views.object_detail, name='reagent_detail'),
path('objects/create/', views.object_create, name='object_create'),
path('objects/<int:pk>/edit/', views.object_update, name='object_update'),
```

---

## Пагинация (+ try, except)

### Что это?
Пагинация - разбиение больших списков данных на страницы. Try/except обрабатывает ошибки неверных номеров страниц.

### Назначение:
- Улучшение производительности
- Снижение нагрузки на БД
- Улучшение UX для больших списков
- Обработка некорректного ввода

### Примеры в проекте:

**Пример 1: Импорт Paginator**
```12:12:intranet/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
```

**Пример 2: Пагинация с обработкой ошибок (полный пример)**
```127:137:intranet/views.py
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
```
*Обрабатывает случаи: страница не число (PageNotAnInteger), страница вне диапазона (EmptyPage).*

**Пример 3: Простая пагинация без явного try/except**
```184:187:intranet/views.py
# Пагинация
paginator = Paginator(reagents_list, 15)
page = request.GET.get('page')
reagents = paginator.get_page(page)
```
*`get_page()` автоматически обрабатывает ошибки (возвращает первую страницу при ошибке).*

**Пример 4: Пагинация задач**
```374:376:intranet/views.py
paginator = Paginator(tasks, 20)
page = request.GET.get('page')
tasks_page = paginator.get_page(page)
```

**Пример 5: Пагинация документов**
```530:532:intranet/views.py
paginator = Paginator(documents, 20)
page = request.GET.get('page')
documents_page = paginator.get_page(page)
```

**Пример 6: Пагинация культур**
```561:563:intranet/views.py
paginator = Paginator(cultures, 15)
page = request.GET.get('page')
cultures_page = paginator.get_page(page)
```

**Разница между подходами:**

```python
# 1. С явной обработкой ошибок (больше контроля)
try:
    page_obj = paginator.page(page)
except PageNotAnInteger:
    page_obj = paginator.page(1)  # Первая страница
except EmptyPage:
    page_obj = paginator.page(paginator.num_pages)  # Последняя страница

# 2. Автоматическая обработка (проще, но меньше контроля)
page_obj = paginator.get_page(page)  # Всегда возвращает валидную страницу
```

**Использование в шаблоне:**

```django
{% for item in page_obj %}
    {{ item }}
{% endfor %}

{# Навигация #}
<div class="pagination">
    {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}">← Назад</a>
    {% endif %}
    
    <span>Страница {{ page_obj.number }} из {{ page_obj.paginator.num_pages }}</span>
    
    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">Вперед →</a>
    {% endif %}
</div>
```

---

## Функция агрегирования

### Что это?
Агрегирующие функции выполняют вычисления на наборе строк и возвращают одно значение (Count, Sum, Avg, Min, Max).

### Назначение:
- Вычисление статистики
- Подсчет количества записей
- Суммы, средние значения
- Группировка данных

### Примеры в проекте:

**Пример 1: Импорт агрегирующих функций**
```13:13:intranet/views.py
from django.db.models import Q, Count, F, Avg, Sum
```

**Пример 2: Count() для подсчета движений по типам**
```123:125:intranet/views.py
movements_stats = ReagentMovement.objects.values('movement_type').annotate(
    total=Count('id')
)
```
*Возвращает количество движений для каждого типа (приход/расход).*

**Результат:**
```python
[
    {'movement_type': 'in', 'total': 45},
    {'movement_type': 'out', 'total': 32}
]
```

**Пример 3: Простой count()**
```113:119:intranet/views.py
stats = {
    'total_reagents': Reagent.objects.count(),
    'total_tasks': Task.objects.filter(assignee=request.user).count(),
    'active_cultures': Culture.objects.filter(status='active').count(),
    'pending_tasks': Task.objects.filter(
        assignee=request.user,
        status='new'
```

**Пример 4: Count в шаблонных тегах**
```26:26:intranet/templatetags/intranet_tags.py
return tasks.count()
```

**Пример 5: Count с условиями**
```74:74:intranet/views.py
'announcements_count': announcements_found.count(),
```

**Дополнительные примеры агрегации (можно добавить в проект):**

```python
# Sum - сумма
total_quantity = ReagentMovement.objects.filter(
    movement_type='in'
).aggregate(total=Sum('quantity'))
# Результат: {'total': 450.5}

# Avg - среднее
avg_price = Reagent.objects.aggregate(avg_price=Avg('on_hand'))
# Результат: {'avg_price': 25.3}

# Min/Max - минимум/максимум
price_range = Reagent.objects.aggregate(
    min_price=Min('on_hand'),
    max_price=Max('on_hand')
)
# Результат: {'min_price': 0, 'max_price': 500}

# Несколько агрегаций одновременно
stats = Task.objects.aggregate(
    total=Count('id'),
    high_priority=Count('id', filter=Q(priority='high')),
    avg_per_user=Count('id') / Count('assignee', distinct=True)
)
```

**Разница между aggregate() и annotate():**

```python
# aggregate() - возвращает словарь с итоговыми значениями
result = Reagent.objects.aggregate(total=Count('id'))
# {'total': 150}

# annotate() - добавляет вычисляемое поле к каждому объекту
reagents = Reagent.objects.annotate(movement_count=Count('movements'))
# Каждый реагент получит поле movement_count
```

---

## Создание простого шаблонного тега

### Что это?
Простой шаблонный тег (`@register.simple_tag`) - это функция Python, которую можно вызвать в шаблоне для получения значения.

### Назначение:
- Вынос сложной логики из шаблонов
- Повторное использование кода
- Динамические вычисления
- Работа с БД из шаблонов

### Примеры в проекте:

**Регистрация библиотеки тегов:**
```10:10:intranet/templatetags/intranet_tags.py
register = template.Library()
```

**Пример 1: Подсчет незавершенных задач**
```17:26:intranet/templatetags/intranet_tags.py
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
```

**Использование:**
```django
{% load intranet_tags %}
Незавершенных задач: {% count_pending_tasks user %}
```

**Пример 2: Подсчет объявлений**
```29:34:intranet/templatetags/intranet_tags.py
@register.simple_tag
def count_announcements():
    """
    Подсчитывает общее количество объявлений
    """
    return Announcement.objects.count()
```

**Пример 3: Подсчет критических реагентов**
```37:43:intranet/templatetags/intranet_tags.py
@register.simple_tag
def count_critical_reagents():
    """
    Подсчитывает количество критических реагентов
    """
    from django.db.models import F
    return Reagent.objects.filter(on_hand__lt=F('min_threshold')).count()
```

**Пример 4: Получение статистики пользователя**
```147:168:intranet/templatetags/intranet_tags.py
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
```

**Использование:**
```django
{% get_user_stats user as stats %}
<p>Всего задач: {{ stats.total_tasks }}</p>
<p>В ожидании: {{ stats.pending_tasks }}</p>
```

**Пример 5: Получение последних объявлений**
```171:178:intranet/templatetags/intranet_tags.py
@register.simple_tag
def get_latest_announcements(count=5):
    """
    Возвращает последние объявления
    """
    return Announcement.objects.select_related('author').order_by(
        '-is_pinned', '-published_at'
    )[:count]
```

---

## Создание шаблонного тега с контекстными переменными

### Что это?
Шаблонный тег с контекстом (`takes_context=True`) имеет доступ к контексту шаблона (request, user, и т.д.).

### Назначение:
- Доступ к request и session
- Работа с текущим пользователем
- Динамическое поведение на основе контекста
- Проверка условий страницы

### Примеры в проекте:

**Пример 1: Проверка активного пункта меню**
```50:60:intranet/templatetags/intranet_tags.py
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
```

**Использование:**
```django
{% load intranet_tags %}
<li class="{% active_menu_item 'dashboard' %}">
    <a href="{% url 'dashboard' %}">Главная</a>
</li>
<li class="{% active_menu_item 'task_list' %}">
    <a href="{% url 'task_list' %}">Задачи</a>
</li>
```

**Пример 2: Приветствие пользователя с учетом времени суток**
```63:85:intranet/templatetags/intranet_tags.py
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
```

**Использование:**
```django
<h1>{% user_greeting %}</h1>
```

**Пример 3: Inclusion tag с контекстом**
```106:124:intranet/templatetags/intranet_tags.py
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
```

**Что доступно в контексте:**
- `request` - объект запроса
- `user` - текущий пользователь
- `request.session` - сессия
- `request.GET`, `request.POST` - параметры
- Любые переменные, переданные в render()

---

## Создание шаблонного тега, возвращающего набор запросов

### Что это?
Inclusion tag (`@register.inclusion_tag`) рендерит отдельный шаблон и возвращает QuerySet или данные для него.

### Назначение:
- Создание виджетов
- Переиспользуемые компоненты
- Инкапсуляция HTML + логики
- Модульная структура шаблонов

### Примеры в проекте:

**Пример 1: Виджет закрепленных объявлений**
```92:103:intranet/templatetags/intranet_tags.py
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
```

**Шаблон виджета (`templates/widgets/pinned_announcements.html`):**
```django
<div class="pinned-announcements">
    <h3>Закрепленные объявления</h3>
    {% for announcement in announcements %}
        <div class="announcement">
            <h4>{{ announcement.title }}</h4>
            <p>{{ announcement.text }}</p>
            <small>{{ announcement.author }} - {{ announcement.published_at }}</small>
        </div>
    {% empty %}
        <p>Нет закрепленных объявлений</p>
    {% endfor %}
</div>
```

**Использование:**
```django
{% load intranet_tags %}
{% show_pinned_announcements %}
```

**Пример 2: Виджет последних задач (с контекстом)**
```106:124:intranet/templatetags/intranet_tags.py
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
```

**Использование:**
```django
{% show_recent_tasks 10 %}  {# С параметром limit=10 #}
{% show_recent_tasks %}     {# С дефолтным limit=5 #}
```

**Пример 3: Виджет критических реагентов**
```127:140:intranet/templatetags/intranet_tags.py
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
```

**Преимущества inclusion_tag:**
1. **Модульность** - виджет можно использовать на разных страницах
2. **Читаемость** - HTML отделен от логики
3. **DRY** - нет дублирования кода
4. **Гибкость** - легко настроить через параметры

**Структура файлов:**
```
templates/
├── widgets/
│   ├── pinned_announcements.html
│   ├── recent_tasks.html
│   └── critical_reagents.html
```

---

## Аутентификация и регистрация пользователя

### Что это?
Система входа (login), выхода (logout) и регистрации новых пользователей в Django.

### Назначение:
- Безопасный вход в систему
- Управление сессиями
- Регистрация новых пользователей
- Защита view через @login_required

### Примеры в проекте:

**Импорт необходимых функций:**
```7:7:intranet/views.py
from django.contrib.auth import login, logout, authenticate
```

```8:8:intranet/views.py
from django.contrib.auth.decorators import login_required
```

### 1. Вход в систему (Login)

**Пример: login_view**
```416:448:intranet/views.py
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
```

**Основные шаги:**
1. `authenticate()` - проверка учетных данных
2. `login()` - создание сессии
3. Сохранение данных в session
4. Redirect на защищенную страницу

### 2. Выход из системы (Logout)

**Пример: logout_view**
```451:457:intranet/views.py
def logout_view(request):
    """
    Выход из системы
    """
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')
```

### 3. Регистрация пользователя (Register)

**Пример: register_view**
```460:490:intranet/views.py
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
```

### 4. Защита view с помощью @login_required

**Пример: dashboard (требует авторизации)**
```35:36:intranet/views.py
@login_required
@cache_page(60 * 5)  # Кеш на 5 минут
def dashboard(request):
```

**Другие примеры:**
```159:160:intranet/views.py
@login_required
def object_list(request):
```

```201:202:intranet/views.py
@login_required
def object_detail(request, pk):
```

### Маршруты аутентификации:

```15:19:intranet/urls.py
# АУТЕНТИФИКАЦИЯ
# ========================================
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('register/', views.register_view, name='register'),
```

### Работа с сессиями:

**Сохранение данных в сессию:**
```434:434:intranet/views.py
request.session['login_time'] = timezone.now().isoformat()
```

```478:479:intranet/views.py
request.session['is_new_user'] = True
request.session['registration_date'] = timezone.now().isoformat()
```

**Получение из сессии (в шаблоне или view):**
```python
# В view
login_time = request.session.get('login_time')
is_new = request.session.get('is_new_user', False)

# В шаблоне
{{ request.session.login_time }}
```

### Проверка авторизации:

```python
# В view
if request.user.is_authenticated:
    # Пользователь авторизован
    username = request.user.username
    
# В шаблоне
{% if user.is_authenticated %}
    <p>Привет, {{ user.username }}!</p>
{% else %}
    <a href="{% url 'login' %}">Войти</a>
{% endif %}
```

### Перенаправление после входа:

```438:440:intranet/views.py
# Перенаправление на следующую страницу или дашборд
next_url = request.GET.get('next', 'dashboard')
return redirect(next_url)
```

**Использование в URL:**
```
/login/?next=/tasks/
```
*После входа пользователь будет перенаправлен на /tasks/*

---

## Итоговая шпаргалка

| Тема | Файл | Строки | Ключевые концепции |
|------|------|--------|-------------------|
| `__str__` | `models.py` | 50-51, 131-132, 191-192 | Строковое представление объектов |
| `timezone` | `models.py`, `views.py` | 9, 176, 146 | timezone.now(), timezone-aware даты |
| `Meta: ordering` | `models.py` | 48, 129, 189, 258, 465 | Сортировка по умолчанию |
| `choices` | `models.py` | 21-31, 70-84, 155-175 | Предопределенные значения полей |
| `related_name` | `models.py` | 163, 182, 248, 342 | Обратные связи ForeignKey |
| `filter()` | `views.py` | 87-91, 101-103, 106-109 | Фильтрация QuerySet |
| `__` (lookup) | `views.py` | 54-56, 94-96, 106-108 | icontains, lt, gte, lte |
| `__` (связи) | `views.py` | 82-84, 211-213 | author__username |
| `exclude()` | `views.py` | 89-91, 94-97, 360-362 | Исключение из QuerySet |
| `order_by()` | `views.py` | 82-84, 101-103, 181-182 | Динамическая сортировка |
| Менеджер | `models.py` | 58-63, 122-124 | ActiveReagentManager |
| `get_object_or_404` | `views.py` | 211-213, 279, 313 | Безопасное получение объекта |
| Фильтры | `intranet_tags.py` | 185-205, 208-225 | pluralize_ru, status_badge |
| `get_absolute_url` | `models.py` | 134-136, 263-264 | URL объекта |
| `reverse` | `views.py`, `models.py` | 323, 136 | Построение URL |
| Пагинация | `views.py` | 127-137, 184-187 | try/except, get_page() |
| Агрегация | `views.py` | 123-125 | Count, annotate |
| Простой тег | `intranet_tags.py` | 17-26, 29-34, 37-43 | @simple_tag |
| Тег с контекстом | `intranet_tags.py` | 50-60, 63-85 | takes_context=True |
| Inclusion tag | `intranet_tags.py` | 92-103, 106-124, 127-140 | Виджеты, QuerySet |
| Аутентификация | `views.py` | 416-448, 451-457, 460-490 | login, logout, register |

---

## Дополнительные вопросы для глубокого понимания

### 1. Почему нужно использовать timezone.now() вместо datetime.now()?
- **Ответ:** `timezone.now()` возвращает timezone-aware datetime, что критично для проектов с пользователями из разных часовых поясов.

### 2. В чем разница между filter() и exclude()?
- **filter()** - возвращает объекты, соответствующие условию
- **exclude()** - возвращает объекты, НЕ соответствующие условию

### 3. Когда использовать get_object_or_404 вместо get()?
- **Всегда в view-функциях!** Это улучшает UX и правильно обрабатывает HTTP-коды.

### 4. Зачем нужен related_name?
- Позволяет обращаться к связанным объектам с понятным именем
- Избегает конфликтов при множественных ForeignKey на одну модель

### 5. В чем разница между simple_tag и inclusion_tag?
- **simple_tag** - возвращает значение (число, строку, объект)
- **inclusion_tag** - рендерит отдельный HTML-шаблон

### 6. Что возвращает annotate(), а что aggregate()?
- **annotate()** - добавляет вычисляемое поле к каждому объекту QuerySet
- **aggregate()** - возвращает словарь с итоговым значением

### 7. Зачем создавать кастомные менеджеры?
- Инкапсуляция повторяющихся запросов
- Упрощение кода view
- Семантическое именование (`active`, `published`, etc.)

