# Лабораторная Django 4 - Навигация по реализации

## Содержание

1. [models.ManyToManyField](#modelsmanyto ManyField)
2. [Chaining filters](#chaining-filters)
3. [__icontains и __contains](#__icontains-и-__contains)
4. [Limiting QuerySets](#limiting-querysets)
5. [values(), values_list()](#values-values_list)
6. [count(), exists()](#count-exists)
7. [update(), delete()](#update-delete)
8. [forms.CharField(widget=forms.Textarea)](#formscharfieldwidgetformstextarea)
9. [form.is_valid() и form.cleaned_data](#formis_valid-и-formcleaned_data)
10. [HttpResponseRedirect](#httpresponseredirect)
11. [{{ field.errors }} {{ field.label_tag }} {{ field }}](#field-в-шаблонах)
12. [fields, exclude, widgets, labels, help_texts, error_messages](#meta-параметры-форм)
13. [request.FILES](#requestfiles)
14. [class Media](#class-media)
15. [F expressions](#f-expressions)
16. [Http404 exception](#http404-exception)
17. [File Uploads](#file-uploads)

---

## models.ManyToManyField

### Простой ManyToMany

**CalendarEvent.participants - Участники события:**
```553:558:intranet/models.py
participants = models.ManyToManyField(
    User,
    related_name='calendar_events',
    blank=True,
    verbose_name='Участники'
)
```

### ManyToMany через through

**Recipe.reagents - Реагенты рецептуры:**
```245:249:intranet/models.py
reagents = models.ManyToManyField(
    Reagent,
    through='RecipeReagent',
    related_name='used_in_recipes',
    verbose_name='Реагенты'
)
```

**Промежуточная модель RecipeReagent:**
```267:308:intranet/models.py
class RecipeReagent(models.Model):
    """
    Промежуточная модель для связи рецептуры и реагентов (through)
    """
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
    
    class Meta:
        verbose_name = 'Реагент в рецептуре'
        verbose_name_plural = 'Реагенты в рецептурах'
        unique_together = ['recipe', 'reagent']
    
    def __str__(self):
        return f"{self.reagent.name}: {self.quantity} {self.get_unit_display()}"
```

**В админке (filter_horizontal):**
```436:436:intranet/admin.py
filter_horizontal = ['participants']
```

---

## Chaining filters

### Пример 1: Задачи пользователя без выполненных
```87:91:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
).exclude(
    status='done'
).select_related('creator').order_by('deadline', '-priority')[:5]
```

### Пример 2: Просроченные задачи
```94:97:intranet/views.py
overdue_tasks_count = Task.objects.filter(
    assignee=request.user,
    deadline__lt=timezone.now()
).exclude(status='done').count()
```

### Пример 3: Фильтрация с условием
```171:178:intranet/views.py
reagents_list = Reagent.objects.all()

category = request.GET.get('category')
if category:
    reagents_list = reagents_list.filter(category=category)

if request.GET.get('critical') == 'true':
    reagents_list = reagents_list.filter(on_hand__lt=F('min_threshold'))
```

---

## __icontains и __contains

### __icontains (регистронезависимый)
```54:57:intranet/views.py
reagents = Reagent.objects.filter(
    Q(name__icontains=search_query) | 
    Q(category__contains=search_query)
).values('id', 'name', 'category')[:5]
```

```60:63:intranet/views.py
tasks = Task.objects.filter(
    Q(title__icontains=search_query) |
    Q(description__icontains=search_query)
).values_list('id', 'title', 'status')[:5]
```

```66:69:intranet/views.py
announcements_found = Announcement.objects.filter(
    Q(title__icontains=search_query) |
    Q(text__icontains=search_query)
)
```

---

## Limiting QuerySets

### Срезы [:N]
```82:84:intranet/views.py
latest_announcements = Announcement.objects.select_related('author').order_by(
    '-is_pinned', '-published_at'
)[:5]
```

```87:91:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
).exclude(
    status='done'
).select_related('creator').order_by('deadline', '-priority')[:5]
```

```101:103:intranet/views.py
critical_reagents = Reagent.objects.filter(
    on_hand__lt=F('min_threshold')
).order_by('on_hand')[:5]
```

```106:109:intranet/views.py
expiring_soon = Reagent.objects.filter(
    expiry_date__lte=timezone.now().date() + timedelta(days=30),
    expiry_date__gte=timezone.now().date()
).order_by('expiry_date')[:5]
```

### first(), last()
```217:217:intranet/views.py
recent_movements = reagent.movements.all()[:10]
```

---

## values(), values_list()

### values() - возвращает словари
```54:57:intranet/views.py
reagents = Reagent.objects.filter(
    Q(name__icontains=search_query) | 
    Q(category__contains=search_query)
).values('id', 'name', 'category')[:5]
```

```123:125:intranet/views.py
movements_stats = ReagentMovement.objects.values('movement_type').annotate(
    total=Count('id')
)
```

```400:402:intranet/views.py
reagents_data = Reagent.objects.values(
    'id', 'name', 'category', 'on_hand', 'min_threshold'
).filter(on_hand__gt=0).order_by('name')[:50]
```

### values_list() - возвращает кортежи
```60:63:intranet/views.py
tasks = Task.objects.filter(
    Q(title__icontains=search_query) |
    Q(description__icontains=search_query)
).values_list('id', 'title', 'status')[:5]
```

```397:397:intranet/views.py
categories = Reagent.objects.values_list('category', flat=True).distinct()
```

---

## count(), exists()

### count()
```74:74:intranet/views.py
'announcements_count': announcements_found.count(),
```

```94:97:intranet/views.py
overdue_tasks_count = Task.objects.filter(
    assignee=request.user,
    deadline__lt=timezone.now()
).exclude(status='done').count()
```

```113:119:intranet/views.py
stats = {
    'total_reagents': Reagent.objects.count(),
    'total_tasks': Task.objects.filter(assignee=request.user).count(),
    'active_cultures': Culture.objects.filter(status='active').count(),
    'pending_tasks': Task.objects.filter(
        assignee=request.user,
        status='new'
    ).count(),
}
```

### exists()
```75:75:intranet/views.py
'announcements_exist': announcements_found.exists(),
```

---

## update(), delete()

### update()
```369:371:intranet/views.py
task_ids = request.POST.getlist('task_ids')
Task.objects.filter(id__in=task_ids).update(status='done')
messages.success(request, f'Отмечено выполненными: {len(task_ids)} задач')
```

```205:210:intranet/models.py
if self.movement_type == 'in':
    Reagent.objects.filter(pk=self.reagent.pk).update(
        on_hand=F('on_hand') + self.quantity
    )
elif self.movement_type == 'out':
    Reagent.objects.filter(pk=self.reagent.pk).update(
```

### delete()
```320:322:intranet/views.py
reagent_name = reagent.name
reagent.delete()
messages.success(request, f'Реагент "{reagent_name}" удален')
```

---

## forms.CharField(widget=forms.Textarea)

### Пример 1: ReagentForm.description (неявно через Meta)
```203:207:intranet/forms.py
'description': forms.Textarea(attrs={
    'class': 'form-control',
    'rows': 5,
    'placeholder': 'Подробное описание рецептуры'
}),
```

### Пример 2: TaskForm
```317:320:intranet/forms.py
'description': forms.Textarea(attrs={
    'class': 'form-control',
    'rows': 5,
    'placeholder': 'Подробное описание задачи'
}),
```

### Пример 3: AnnouncementForm
```396:399:intranet/forms.py
'text': forms.Textarea(attrs={
    'class': 'form-control',
    'rows': 6,
    'placeholder': 'Текст объявления'
}),
```

---

## form.is_valid() и form.cleaned_data

### Создание объекта
```253:258:intranet/views.py
if request.method == 'POST':
    form = ReagentForm(request.POST, request.FILES)
    if form.is_valid():
        reagent = form.save()
        messages.success(request, f'Реагент "{reagent.name}" успешно создан')
        return HttpResponseRedirect(reagent.get_absolute_url())
```

### Редактирование
```286:291:intranet/views.py
if request.method == 'POST':
    form = ReagentForm(request.POST, request.FILES, instance=reagent)
    if form.is_valid():
        updated_reagent = form.save(commit=True)
        messages.success(request, f'Реагент "{updated_reagent.name}" обновлен')
        return HttpResponseRedirect(updated_reagent.get_absolute_url())
```

### cleaned_data в login
```424:428:intranet/views.py
if form.is_valid():
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user = authenticate(request, username=username, password=password)
```

### Валидация в clean методах
```145:150:intranet/forms.py
expiry_date = self.cleaned_data.get('expiry_date')
if expiry_date and expiry_date < timezone.now().date():
    raise forms.ValidationError(
        'Срок годности не может быть в прошлом'
    )
return expiry_date
```

---

## HttpResponseRedirect

```10:10:intranet/views.py
from django.http import HttpResponseRedirect, Http404, HttpResponse
```

```258:258:intranet/views.py
return HttpResponseRedirect(reagent.get_absolute_url())
```

```291:291:intranet/views.py
return HttpResponseRedirect(updated_reagent.get_absolute_url())
```

```323:323:intranet/views.py
return HttpResponseRedirect(reverse('object_list'))
```

---

## field в шаблонах

### Использование в шаблонах (типичный паттерн Django):

```django
{# Базовый паттерн #}
<div class="form-group">
    {{ field.label_tag }}
    {{ field }}
    {% if field.errors %}
        <div class="invalid-feedback">
            {{ field.errors }}
        </div>
    {% endif %}
</div>

{# С Bootstrap классами #}
<div class="mb-3">
    <label for="{{ field.id_for_label }}" class="form-label">
        {{ field.label }}
    </label>
    {{ field }}
    {% if field.errors %}
        <div class="text-danger">
            {{ field.errors.as_text }}
        </div>
    {% endif %}
</div>
```

---

## Meta параметры форм

### Полный пример: ReagentForm

**fields:**
```87:90:intranet/forms.py
fields = [
    'name', 'category', 'on_hand', 'min_threshold',
    'expiry_date', 'image', 'certificate', 'external_link'
]
```

**widgets:**
```91:115:intranet/forms.py
widgets = {
    'name': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Название реагента'
    }),
    'category': forms.Select(attrs={'class': 'form-select'}),
    'on_hand': forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01'
    }),
    'min_threshold': forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01'
    }),
    'expiry_date': forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }),
    'image': forms.FileInput(attrs={'class': 'form-control'}),
    'certificate': forms.FileInput(attrs={'class': 'form-control'}),
    'external_link': forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://example.com'
    }),
}
```

**labels:**
```116:125:intranet/forms.py
labels = {
    'name': 'Название',
    'category': 'Категория',
    'on_hand': 'Остаток на складе',
    'min_threshold': 'Минимальный порог',
    'expiry_date': 'Срок годности',
    'image': 'Изображение',
    'certificate': 'Сертификат',
    'external_link': 'Внешняя ссылка',
}
```

**help_texts:**
```126:130:intranet/forms.py
help_texts = {
    'on_hand': 'Текущее количество на складе',
    'min_threshold': 'При достижении этого значения реагент считается критичным',
    'expiry_date': 'Дата окончания срока годности',
}
```

**error_messages:**
```131:139:intranet/forms.py
error_messages = {
    'name': {
        'required': 'Пожалуйста, укажите название реагента',
        'max_length': 'Название слишком длинное',
    },
    'category': {
        'required': 'Выберите категорию реагента',
    },
}
```

---

## request.FILES

### В view для создания
```254:254:intranet/views.py
form = ReagentForm(request.POST, request.FILES)
```

### В view для редактирования
```287:287:intranet/views.py
form = ReagentForm(request.POST, request.FILES, instance=reagent)
```

### Загрузка документа
```506:506:intranet/views.py
form = DocumentTemplateForm(request.POST, request.FILES)
```

**Важно:** Без `request.FILES` файлы не будут обработаны!

---

## class Media

### RecipeForm с Media
```211:218:intranet/forms.py
class Media:
    """
    Подключение дополнительных JS/CSS для формы
    """
    css = {
        'all': ('css/recipe-form.css',)
    }
    js = ('js/recipe-form.js',)
```

**Использование:**
- Автоматически подключает CSS/JS при рендеринге формы
- `{{ form.media }}` в шаблоне
- Порядок загрузки контролируется Django

---

## F expressions

### В модели для атомарного обновления
```10:10:intranet/models.py
from django.db.models import F
```

```205:210:intranet/models.py
if self.movement_type == 'in':
    Reagent.objects.filter(pk=self.reagent.pk).update(
        on_hand=F('on_hand') + self.quantity
    )
elif self.movement_type == 'out':
    Reagent.objects.filter(pk=self.reagent.pk).update(
        on_hand=F('on_hand') - self.quantity
```

### В view для фильтрации
```101:103:intranet/views.py
critical_reagents = Reagent.objects.filter(
    on_hand__lt=F('min_threshold')
).order_by('on_hand')[:5]
```

```177:178:intranet/views.py
if request.GET.get('critical') == 'true':
    reagents_list = reagents_list.filter(on_hand__lt=F('min_threshold'))
```

**Преимущества:**
- Атомарные операции в БД
- Избегание race conditions
- Производительность

---

## Http404 exception

### Импорт
```10:10:intranet/views.py
from django.http import HttpResponseRedirect, Http404, HttpResponse
```

### Использование
```251:251:intranet/views.py
raise Http404("У вас нет прав для создания реагентов")
```

```317:317:intranet/views.py
raise Http404("Только системный администратор может удалять реагенты")
```

### get_object_or_404 (предпочтительный способ)
```6:6:intranet/views.py
from django.shortcuts import render, redirect, get_object_or_404
```

```211:213:intranet/views.py
reagent = get_object_or_404(
    Reagent.objects.prefetch_related('movements__user'),
    pk=pk
)
```

```279:279:intranet/views.py
reagent = get_object_or_404(Reagent, pk=pk)
```

```313:313:intranet/views.py
reagent = get_object_or_404(Reagent, pk=pk)
```

---

## File Uploads

### ImageField в модели
```33:38:intranet/models.py
avatar = models.ImageField(
    'Аватар',
    upload_to='avatars/',
    blank=True,
    null=True
)
```

```102:107:intranet/models.py
image = models.ImageField(
    'Изображение',
    upload_to='reagents/',
    blank=True,
    null=True
)
```

### FileField в модели
```108:113:intranet/models.py
certificate = models.FileField(
    'Сертификат',
    upload_to='certificates/',
    blank=True,
    null=True
)
```

```576:578:intranet/models.py
file = models.FileField(
    'Файл',
    upload_to='documents/'
)
```

### Настройка медиа в settings
```145:147:ddc_intranet/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Раздача медиа в urls
```19:19:ddc_intranet/urls.py
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### В формах
```109:110:intranet/forms.py
'image': forms.FileInput(attrs={'class': 'form-control'}),
'certificate': forms.FileInput(attrs={'class': 'form-control'}),
```

### В view с request.FILES
```254:254:intranet/views.py
form = ReagentForm(request.POST, request.FILES)
```

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

---

## Итоговая таблица

| Тема | Файл | Строки |
|------|------|--------|
| ManyToManyField | models.py | 245-249, 553-558 |
| Chaining | views.py | 87-91, 94-97 |
| __icontains | views.py | 54-57, 60-63 |
| Limiting [:N] | views.py | 82-84, 101-103 |
| values() | views.py | 54-57, 400-402 |
| count() | views.py | 74, 94-97 |
| update() | views.py | 369-371 |
| Textarea widget | forms.py | 203-207, 317-320 |
| is_valid() | views.py | 253-258, 286-291 |
| HttpResponseRedirect | views.py | 258, 291, 323 |
| Meta форм | forms.py | 87-139 |
| request.FILES | views.py | 254, 287, 506 |
| class Media | forms.py | 211-218 |
| F expressions | models.py, views.py | 205-210, 101-103 |
| Http404 | views.py | 251, 317 |
| File Uploads | models.py | 33-38, 102-113 |

