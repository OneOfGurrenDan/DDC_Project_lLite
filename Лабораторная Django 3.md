# Лабораторная Django 3 - Навигация по реализации

## Содержание

### Пункты лабораторной работы:
1. [verbose_name и verbose_name_plural в Meta](#verbose_name-и-verbose_name_plural)
2. [models.ImageField и библиотека Pillow](#modelsimagefield-и-pillow)
3. [Использование сеансов Django](#использование-сеансов-django)
4. [return redirect в view](#return-redirect-в-view)
5. [inlines в админке](#inlines-в-админке)
6. [Генерация PDF документа в админке](#генерация-pdf-в-админке)
7. [models.FileField](#modelsfilefield)
8. [models.URLField()](#modelsurlfield)

### Вопросы:
9. [Создание собственного функционального метода в модели](#собственные-методы-в-модели)
10. [Добавить действие на сайт администрирования](#действия-в-админке-actions)
11. [Интернационализация в Django](#интернационализация)
12. [Раздача медиафайлов](#раздача-медиафайлов)
13. [Использование кеш-фреймворка](#использование-кеша)

---

## verbose_name и verbose_name_plural

### Что это?
Атрибуты в `class Meta` модели для человекочитаемых названий модели в единственном и множественном числе.

### Назначение:
- Отображение в админ-панели
- Использование в шаблонах
- Читаемые сообщения
- Локализация интерфейса

### Примеры в проекте:

**User:**
```45:48:intranet/models.py
class Meta:
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'
    ordering = ['username']
```

**Reagent:**
```126:129:intranet/models.py
class Meta:
    verbose_name = 'Реагент'
    verbose_name_plural = 'Реагенты'
    ordering = ['name']
```

**ReagentMovement:**
```186:189:intranet/models.py
class Meta:
    verbose_name = 'Движение реагента'
    verbose_name_plural = 'Движения реагентов'
    ordering = ['-date']
```

**Recipe:**
```255:258:intranet/models.py
class Meta:
    verbose_name = 'Рецептура'
    verbose_name_plural = 'Рецептуры'
    ordering = ['-created_at']
```

**RecipeReagent:**
```301:304:intranet/models.py
class Meta:
    verbose_name = 'Реагент в рецептуре'
    verbose_name_plural = 'Реагенты в рецептурах'
    unique_together = ['recipe', 'reagent']
```

**Culture:**
```353:356:intranet/models.py
class Meta:
    verbose_name = 'Культура'
    verbose_name_plural = 'Культуры'
    ordering = ['-seeding_date']
```

**Task:**
```462:465:intranet/models.py
class Meta:
    verbose_name = 'Задача'
    verbose_name_plural = 'Задачи'
    ordering = ['deadline', '-priority']
```

**Announcement:**
```529:532:intranet/models.py
class Meta:
    verbose_name = 'Объявление'
    verbose_name_plural = 'Объявления'
    ordering = ['-is_pinned', '-published_at']
```

### Где используется:
- В админ-панели (заголовки разделов)
- В сообщениях Django
- В шаблонах через `{% verbose_name %}`
- В формах (автоматические лейблы)

---

## models.ImageField и Pillow

### Что это?
`ImageField` - поле для хранения изображений. Требует установки библиотеки Pillow.

### Зависимость:
```3:3:requirements.txt
Pillow==10.4.0
```

### Примеры в проекте:

#### 1. User.avatar - Аватар пользователя

```33:38:intranet/models.py
avatar = models.ImageField(
    'Аватар',
    upload_to='avatars/',
    blank=True,
    null=True
)
```

**Админка с превью:**
```46:54:intranet/admin.py
@admin.display(description='Аватар')
def avatar_preview(self, obj):
    """Превью аватара в списке"""
    if obj.avatar:
        return format_html(
            '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />',
            obj.avatar.url
        )
    return '—'
```

**В list_display:**
```35:35:intranet/admin.py
list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'avatar_preview']
```

#### 2. Reagent.image - Изображение реагента

```102:107:intranet/models.py
image = models.ImageField(
    'Изображение',
    upload_to='reagents/',
    blank=True,
    null=True
)
```

**Маленькое превью в списке:**
```134:142:intranet/admin.py
@admin.display(description='Изображение')
def image_preview(self, obj):
    """Маленькое превью изображения"""
    if obj.image:
        return format_html(
            '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
            obj.image.url
        )
    return '—'
```

**Большое превью в форме редактирования:**
```144:152:intranet/admin.py
@admin.display(description='Превью изображения')
def image_preview_large(self, obj):
    """Большое превью изображения"""
    if obj.image:
        return format_html(
            '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
            obj.image.url
        )
    return 'Нет изображения'
```

**В readonly_fields для просмотра:**
```85:85:intranet/admin.py
readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
```

**Fieldsets с изображением:**
```94:96:intranet/admin.py
('Файлы', {
    'fields': ('image', 'image_preview_large', 'certificate')
}),
```

### Параметры ImageField:
- `upload_to` - директория для загрузки (`'avatars/'`, `'reagents/'`)
- `blank=True` - необязательное поле в формах
- `null=True` - может быть NULL в БД
- `max_length` - максимальная длина пути (по умолчанию 100)
- `width_field`, `height_field` - поля для хранения размеров

### Настройка медиа в settings.py:
```145:147:ddc_intranet/settings.py
# Media files (загруженные пользователями файлы)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Использование в формах:
```109:109:intranet/forms.py
'image': forms.FileInput(attrs={'class': 'form-control'}),
```

### Обработка в view:
```254:254:intranet/views.py
form = ReagentForm(request.POST, request.FILES)
```
*Важно: `request.FILES` обязателен для загрузки файлов!*

---

## Использование сеансов Django

### Что это?
Сеансы (sessions) позволяют хранить данные между HTTP-запросами для конкретного пользователя.

### Настройка в settings.py:
```187:190:ddc_intranet/settings.py
# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 часа
SESSION_SAVE_EVERY_REQUEST = False
```

### Примеры в проекте:

#### 1. Сохранение времени входа

```434:434:intranet/views.py
request.session['login_time'] = timezone.now().isoformat()
```

**Полный контекст:**
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

#### 2. Сохранение информации о регистрации

```478:479:intranet/views.py
request.session['is_new_user'] = True
request.session['registration_date'] = timezone.now().isoformat()
```

**Полный контекст:**
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

#### 3. Сохранение последнего поискового запроса

```78:79:intranet/views.py
# Сохраняем последний поиск в сессию
request.session['last_search'] = search_query
```

### Основные операции с сессиями:

```python
# Сохранение данных
request.session['key'] = 'value'
request.session['user_id'] = 123
request.session['settings'] = {'theme': 'dark', 'lang': 'ru'}

# Получение данных
value = request.session.get('key')
value = request.session.get('key', 'default_value')

# Проверка наличия ключа
if 'key' in request.session:
    ...

# Удаление ключа
del request.session['key']

# Очистка всей сессии
request.session.flush()

# Установка времени жизни
request.session.set_expiry(3600)  # 1 час
request.session.set_expiry(0)     # До закрытия браузера

# Использование в шаблонах
{{ request.session.login_time }}
{{ request.session.is_new_user }}
```

---

## return redirect в view

### Что это?
`redirect()` - функция для перенаправления пользователя на другую страницу.

### Примеры в проекте:

#### 1. Redirect после входа

```421:421:intranet/views.py
return redirect('dashboard')
```

```440:440:intranet/views.py
return redirect(next_url)
```

#### 2. Redirect после выхода

```457:457:intranet/views.py
return redirect('login')
```

#### 3. Redirect после регистрации

```482:482:intranet/views.py
return redirect('dashboard')
```

#### 4. Redirect после создания объекта

```258:258:intranet/views.py
return HttpResponseRedirect(reagent.get_absolute_url())
```

#### 5. Redirect с именем маршрута

```323:323:intranet/views.py
return HttpResponseRedirect(reverse('object_list'))
```

#### 6. Redirect после редактирования

```284:284:intranet/views.py
return redirect('reagent_detail', pk=pk)
```

#### 7. Redirect после загрузки документа

```512:512:intranet/views.py
return redirect('document_list')
```

#### 8. Conditional redirect (проверка прав)

```283:284:intranet/views.py
messages.error(request, 'У вас нет прав для редактирования реагентов')
return redirect('reagent_detail', pk=pk)
```

### Варианты использования redirect:

```python
# 1. По имени URL
return redirect('dashboard')

# 2. С параметрами
return redirect('reagent_detail', pk=5)

# 3. С get-параметрами
return redirect('/tasks/?status=new')

# 4. К методу get_absolute_url модели
return redirect(reagent)  # Если у модели есть get_absolute_url()

# 5. К внешнему URL
return redirect('https://example.com')

# 6. С reverse()
from django.urls import reverse
return redirect(reverse('task_list'))

# 7. HttpResponseRedirect (то же самое)
from django.http import HttpResponseRedirect
return HttpResponseRedirect('/path/')
```

---

## inlines в админке

### Что это?
Inlines позволяют редактировать связанные объекты на одной странице с родительским объектом.

### Типы Inline:
- `TabularInline` - компактное табличное представление
- `StackedInline` - вертикальное представление

### Примеры в проекте:

#### 1. ReagentMovementInline - Движения реагента

```61:70:intranet/admin.py
class ReagentMovementInline(admin.TabularInline):
    """
    Инлайн для отображения движений реагента
    """
    model = ReagentMovement
    extra = 1
    fields = ['movement_type', 'quantity', 'date', 'user', 'comment']
    raw_id_fields = ['user']
    readonly_fields = ['date']
```

**Использование:**
```103:103:intranet/admin.py
inlines = [ReagentMovementInline]
```

#### 2. RecipeReagentInline - Реагенты в рецептуре

```219:226:intranet/admin.py
class RecipeReagentInline(admin.TabularInline):
    """
    Инлайн для реагентов в рецептуре
    """
    model = RecipeReagent
    extra = 2
    raw_id_fields = ['reagent']
```

**Использование:**
```252:252:intranet/admin.py
inlines = [RecipeReagentInline]
```

#### 3. CultureEventInline - События культуры (StackedInline)

```270:278:intranet/admin.py
class CultureEventInline(admin.StackedInline):
    """
    Инлайн для событий культуры
    """
    model = CultureEvent
    extra = 1
    fields = ['event_type', 'date', 'user', 'comment']
    raw_id_fields = ['user']
```

**Использование:**
```292:292:intranet/admin.py
inlines = [CultureEventInline]
```

#### 4. TaskCommentInline - Комментарии к задаче

```311:320:intranet/admin.py
class TaskCommentInline(admin.TabularInline):
    """
    Инлайн для комментариев к задаче
    """
    model = TaskComment
    extra = 1
    fields = ['user', 'text', 'date']
    readonly_fields = ['date']
    raw_id_fields = ['user']
```

**Использование:**
```351:351:intranet/admin.py
inlines = [TaskCommentInline]
```

### Параметры Inline:
- `model` - связанная модель
- `extra` - количество пустых форм
- `fields` - отображаемые поля
- `exclude` - исключаемые поля
- `readonly_fields` - поля только для чтения
- `raw_id_fields` - ForeignKey как ID (с лупой)
- `can_delete` - возможность удаления
- `max_num` - максимум форм
- `min_num` - минимум форм

---

## Генерация PDF в админке

### Что это?
Создание PDF-документов через действия (actions) в админ-панели Django.

### Зависимость:
```5:5:requirements.txt
reportlab==4.2.5
```

### Импорты:
```12:16:intranet/admin.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
```

### Пример реализации:

```154:194:intranet/admin.py
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
```

**Регистрация в actions:**
```105:105:intranet/admin.py
actions = ['export_to_pdf', 'mark_as_critical']
```

### Основные операции ReportLab:

```python
# Создание canvas
p = canvas.Canvas(buffer, pagesize=A4)
width, height = A4

# Текст
p.setFont("Helvetica", 12)
p.drawString(x, y, "Text")

# Жирный текст
p.setFont("Helvetica-Bold", 16)

# Линия
p.line(x1, y1, x2, y2)

# Прямоугольник
p.rect(x, y, width, height)

# Изображение
p.drawImage("path.jpg", x, y, width, height)

# Новая страница
p.showPage()

# Сохранение
p.save()

# Возврат как HTTP response
response = HttpResponse(buffer, content_type='application/pdf')
response['Content-Disposition'] = 'attachment; filename="report.pdf"'
```

---

## models.FileField

### Что это?
Поле для загрузки файлов любого типа.

### Примеры в проекте:

#### 1. Reagent.certificate - Сертификат реагента

```108:113:intranet/models.py
certificate = models.FileField(
    'Сертификат',
    upload_to='certificates/',
    blank=True,
    null=True
)
```

#### 2. DocumentTemplate.file - Файл документа

```576:578:intranet/models.py
file = models.FileField(
    'Файл',
    upload_to='documents/'
)
```

### В формах:

```110:110:intranet/forms.py
'certificate': forms.FileInput(attrs={'class': 'form-control'}),
```

```472:472:intranet/forms.py
'file': forms.FileInput(attrs={'class': 'form-control'}),
```

### В админке со ссылкой на скачивание:

```465:473:intranet/admin.py
@admin.display(description='Файл')
def file_link(self, obj):
    """Ссылка на файл"""
    if obj.file:
        return format_html(
            '<a href="{}" target="_blank">Скачать</a>',
            obj.file.url
        )
    return '—'
```

### В view для загрузки:

```505:512:intranet/views.py
if request.method == 'POST':
    form = DocumentTemplateForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.uploaded_by = request.user
        document.save()
        messages.success(request, 'Документ успешно загружен')
        return redirect('document_list')
```

### Разница ImageField vs FileField:

| Характеристика | FileField | ImageField |
|----------------|-----------|------------|
| Тип файлов | Любые | Только изображения |
| Валидация | Нет | Проверка формата |
| Требует Pillow | Нет | Да |
| Атрибуты width/height | Нет | Да |

---

## models.URLField

### Что это?
Поле для хранения URL-адресов с валидацией.

### Примеры в проекте:

#### 1. User.profile_url - Ссылка на профиль

```39:43:intranet/models.py
profile_url = models.URLField(
    'Ссылка на профиль',
    blank=True,
    null=True
)
```

#### 2. Reagent.external_link - Внешняя ссылка

```114:118:intranet/models.py
external_link = models.URLField(
    'Внешняя ссылка',
    blank=True,
    null=True
)
```

### В формах:

```111:114:intranet/forms.py
'external_link': forms.URLInput(attrs={
    'class': 'form-control',
    'placeholder': 'https://example.com'
}),
```

### Параметры URLField:
- `max_length` - по умолчанию 200
- `blank=True` - необязательное
- `null=True` - может быть NULL
- Автоматическая валидация URL формата

---

## Собственные методы в модели

### Что это?
Кастомные методы модели для бизнес-логики и вычислений.

### Примеры в проекте:

#### 1. Reagent.is_critical() - Проверка критического остатка

```138:140:intranet/models.py
def is_critical(self):
    """Проверяет, критичен ли остаток реагента"""
    return self.on_hand <= self.min_threshold
```

#### 2. Reagent.is_expiring_soon() - Проверка срока годности

```142:147:intranet/models.py
def is_expiring_soon(self):
    """Проверяет, истекает ли срок годности в ближайшие 30 дней"""
    if not self.expiry_date:
        return False
    days_left = (self.expiry_date - timezone.now().date()).days
    return 0 <= days_left <= 30
```

#### 3. Task.is_overdue() - Проверка просрочки задачи

```473:477:intranet/models.py
def is_overdue(self):
    """Проверяет, просрочена ли задача"""
    if not self.deadline:
        return False
    return timezone.now() > self.deadline and self.status != 'done'
```

### Использование в админке:

```127:132:intranet/admin.py
if obj.is_expiring_soon():
    return format_html(
        '<span style="color: red; font-weight: bold;">{}</span>',
        obj.expiry_date.strftime('%d.%m.%Y')
    )
return obj.expiry_date.strftime('%d.%m.%Y')
```

---

## Действия в админке (Actions)

### Что это?
Массовые действия над выбранными объектами в админ-панели.

### Примеры в проекте:

#### 1. export_to_pdf - Экспорт в PDF

```154:194:intranet/admin.py
@admin.action(description='Экспорт в PDF')
def export_to_pdf(self, request, queryset):
    """Генерация PDF с выбранными реагентами"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    # ... генерация PDF ...
    self.message_user(request, f'PDF создан для {queryset.count()} реагентов')
    return response
```

#### 2. mark_as_critical - Отметить как критические

```196:200:intranet/admin.py
@admin.action(description='Отметить как критические (для теста)')
def mark_as_critical(self, request, queryset):
    """Массовое действие для тестирования"""
    count = queryset.update(on_hand=0)
    self.message_user(request, f'{count} реагентов отмечены как критические')
```

#### 3. approve_recipes - Утверждение рецептур

```256:263:intranet/admin.py
@admin.action(description='Утвердить выбранные рецептуры')
def approve_recipes(self, request, queryset):
    """Массовое утверждение рецептур"""
    from django.utils import timezone
    count = queryset.update(status='approved', approved_at=timezone.now())
    self.message_user(request, f'{count} рецептур утверждено')
```

**Регистрация:**
```254:254:intranet/admin.py
actions = ['approve_recipes']
```

---

## Интернационализация

### Настройки в settings.py:

```129:135:ddc_intranet/settings.py
LANGUAGE_CODE = 'ru'  # Русский язык

TIME_ZONE = 'Europe/Moscow'  # Московский часовой пояс

USE_I18N = True

USE_TZ = True
```

### Кастомизация админки:

```476:479:intranet/admin.py
# Кастомизация админ-панели
admin.site.site_header = 'DDC Biotech Интранет'
admin.site.site_title = 'DDC Biotech Admin'
admin.site.index_title = 'Панель управления'
```

---

## Раздача медиафайлов

### Настройка в settings.py:

```145:147:ddc_intranet/settings.py
# Media files (загруженные пользователями файлы)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Настройка в urls.py:

```17:20:ddc_intranet/urls.py
# Обработка статики и медиа в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Импорты:**
```7:8:ddc_intranet/urls.py
from django.conf import settings
from django.conf.urls.static import static
```

### Для продакшна:
Используйте веб-сервер (Nginx, Apache) для раздачи медиафайлов, а не Django.

---

## Использование кеша

### Настройка в settings.py:

```160:171:ddc_intranet/settings.py
# Cache Configuration
# Простой локальный кеш для разработки
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 минут
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
```

### Использование в views:

```35:36:intranet/views.py
@login_required
@cache_page(60 * 5)  # Кеш на 5 минут
def dashboard(request):
```

**Импорт:**
```15:15:intranet/views.py
from django.views.decorators.cache import cache_page
```

### Ручная работа с кешем:

```16:16:intranet/views.py
from django.core.cache import cache
```

```python
# Сохранение в кеш
cache.set('my_key', 'my_value', timeout=300)

# Получение из кеша
value = cache.get('my_key')
value = cache.get('my_key', 'default')

# Удаление
cache.delete('my_key')

# Очистка всего кеша
cache.clear()

# Множественные операции
cache.set_many({'a': 1, 'b': 2})
cache.get_many(['a', 'b'])
```

---

## Итоговая шпаргалка

| Тема | Файл | Строки | Описание |
|------|------|--------|----------|
| **verbose_name** | models.py | 45-48, 126-129 | Названия моделей |
| **ImageField** | models.py | 33-38, 102-107 | Поля изображений |
| **Превью в админке** | admin.py | 46-54, 134-152 | format_html для изображений |
| **Сеансы** | views.py | 434, 478-479 | request.session |
| **redirect** | views.py | 421, 457, 482 | Перенаправления |
| **inlines** | admin.py | 61-70, 219-226, 270-278 | TabularInline, StackedInline |
| **PDF генерация** | admin.py | 154-194 | ReportLab, @admin.action |
| **FileField** | models.py | 108-113, 576-578 | Загрузка файлов |
| **URLField** | models.py | 39-43, 114-118 | URL с валидацией |
| **Методы модели** | models.py | 138-147, 473-477 | is_critical, is_expiring_soon |
| **Actions** | admin.py | 154-200, 256-263 | Массовые действия |
| **i18n** | settings.py | 129-135 | LANGUAGE_CODE, TIME_ZONE |
| **Медиафайлы** | urls.py | 17-20 | static() в DEBUG |
| **Кеш** | settings.py, views.py | 160-171, 35-36 | CACHES, @cache_page |

---

## Контрольные вопросы

1. **Зачем нужны verbose_name и verbose_name_plural?**  
   Для человекочитаемых названий в админке и шаблонах

2. **Какая библиотека нужна для ImageField?**  
   Pillow

3. **Где хранятся данные сеансов Django?**  
   В БД (по умолчанию), можно в файлах или кеше

4. **В чем разница между redirect() и HttpResponseRedirect()?**  
   redirect() более удобен, принимает имя URL, HttpResponseRedirect - только путь

5. **Что такое inlines в админке?**  
   Редактирование связанных объектов на одной странице

6. **Какая библиотека используется для PDF?**  
   ReportLab

7. **В чем разница FileField и ImageField?**  
   ImageField только для изображений, требует Pillow, имеет width/height

8. **Зачем кастомные методы в моделях?**  
   Для бизнес-логики и вычислений, доступных везде

9. **Что делает @admin.action?**  
   Создает массовое действие в админке

10. **Как раздавать медиафайлы в продакшне?**  
    Через веб-сервер (Nginx), а не Django

