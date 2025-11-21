# Лабораторная Django 2 - Навигация по реализации

## Содержание
1. [Создание форм из моделей (ModelForm)](#создание-форм-из-моделей-modelform)
2. [Файл requirements.txt](#файл-requirementstxt)
3. [Использование метода save() в модели](#использование-метода-save-в-модели)
4. [Meta widgets в формах](#meta-widgets-в-формах)
5. [Пример clean_<fieldname>()](#пример-clean_fieldname)
6. [def save с commit=True](#def-save-с-committrue)
7. [models.ManyToManyField с параметром through](#modelsmanyto ManyField-с-параметром-through)
8. [select_related()](#select_related)
9. [prefetch_related()](#prefetch_related)
10. [django-debug-toolbar](#django-debug-toolbar)

---

## Создание форм из моделей (ModelForm)

### Что это?
`ModelForm` - это класс Django, который автоматически создает форму на основе модели. Это упрощает создание форм для CRUD операций (Create, Read, Update, Delete).

### Назначение:
- Автоматическая генерация полей формы из модели
- Валидация данных согласно правилам модели
- Упрощение кода (DRY принцип)
- Автоматическое сохранение в БД

### Примеры в проекте:

#### 1. ReagentForm - Форма для реагентов

**Определение формы:**

```79:162:intranet/forms.py
class ReagentForm(forms.ModelForm):
    """
    Форма для создания/редактирования реагента
    Демонстрация использования widgets, labels, help_texts, error_messages
    """
    
    class Meta:
        model = Reagent
        fields = [
            'name', 'category', 'on_hand', 'min_threshold',
            'expiry_date', 'image', 'certificate', 'external_link'
        ]
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
        help_texts = {
            'on_hand': 'Текущее количество на складе',
            'min_threshold': 'При достижении этого значения реагент считается критичным',
            'expiry_date': 'Дата окончания срока годности',
        }
        error_messages = {
            'name': {
                'required': 'Пожалуйста, укажите название реагента',
                'max_length': 'Название слишком длинное',
            },
            'category': {
                'required': 'Выберите категорию реагента',
            },
        }
    
    def clean_expiry_date(self):
        """
        Валидация срока годности - не должен быть в прошлом
        """
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date < timezone.now().date():
            raise forms.ValidationError(
                'Срок годности не может быть в прошлом'
            )
        return expiry_date
    
    def clean_on_hand(self):
        """
        Валидация остатка - не может быть отрицательным
        """
        on_hand = self.cleaned_data.get('on_hand')
        if on_hand < 0:
            raise forms.ValidationError(
                'Остаток не может быть отрицательным'
            )
        return on_hand
```

**Использование в view для создания:**

```238:267:intranet/views.py
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
```

**Использование в view для редактирования:**

```270:301:intranet/views.py
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
```

**Использование в view для удаления:**

```304:329:intranet/views.py
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
```

#### 2. TaskForm - Форма для задач

```300:356:intranet/forms.py
class TaskForm(forms.ModelForm):
    """
    Форма для создания/редактирования задачи
    Демонстрация кастомного save()
    """
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assignee', 'status',
            'priority', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое описание задачи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Подробное описание задачи'
            }),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def clean_deadline(self):
        """
        Валидация дедлайна - не должен быть в прошлом
        """
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError(
                'Дедлайн не может быть в прошлом'
            )
        return deadline
    
    def save(self, commit=True):
        """
        Кастомный метод save() для автоматической установки создателя
        """
        task = super().save(commit=False)
        
        # Если задача новая и у неё нет создателя, устанавливаем из контекста
        if not task.pk and not task.creator:
            # Создатель будет установлен во view
            pass
        
        if commit:
            task.save()
        
        return task
```

#### 3. RecipeForm - Форма для рецептур

```190:218:intranet/forms.py
class RecipeForm(forms.ModelForm):
    """
    Форма для создания/редактирования рецептуры
    """
    
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название рецептуры'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Подробное описание рецептуры'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    class Media:
        """
        Подключение дополнительных JS/CSS для формы
        """
        css = {
            'all': ('css/recipe-form.css',)
        }
        js = ('js/recipe-form.js',)
```

#### 4. CultureForm - Форма для культур

```243:271:intranet/forms.py
class CultureForm(forms.ModelForm):
    """
    Форма для создания/редактирования культуры
    """
    
    class Meta:
        model = Culture
        fields = [
            'name', 'status', 'seeding_date', 'passage_number',
            'recipe', 'responsible', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название культуры'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'seeding_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'passage_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'recipe': forms.Select(attrs={'class': 'form-select'}),
            'responsible': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
```

#### 5. UserRegisterForm - Форма регистрации

```40:72:intranet/forms.py
class UserRegisterForm(UserCreationForm):
    """
    Форма регистрации нового пользователя
    """
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
```

### Ключевые концепции ModelForm:

1. **Указание модели:** `model = Reagent`
2. **Выбор полей:** `fields = [...]` или `fields = '__all__'`
3. **Исключение полей:** `exclude = [...]`
4. **Настройка виджетов:** `widgets = {...}`
5. **Кастомные лейблы:** `labels = {...}`
6. **Помощь пользователю:** `help_texts = {...}`
7. **Сообщения об ошибках:** `error_messages = {...}`

---

## Файл requirements.txt

### Что это?
`requirements.txt` - это файл, содержащий список всех зависимостей (пакетов Python) проекта с указанием версий.

### Назначение:
- Документирование зависимостей проекта
- Воспроизводимость окружения
- Простая установка всех зависимостей одной командой
- Контроль версий пакетов

### Содержимое файла в проекте:

```1:10:requirements.txt
Django==4.2.16
djangorestframework==3.16.1
Pillow==10.4.0
django-debug-toolbar==4.4.6
reportlab==4.2.5

# PostgreSQL support (раскомментировать при необходимости)
# psycopg2-binary==2.9.9

```

### Описание зависимостей:

| Пакет | Версия | Назначение |
|-------|--------|-----------|
| `Django` | 4.2.16 | Основной фреймворк |
| `djangorestframework` | 3.16.1 | REST API |
| `Pillow` | 10.4.0 | Работа с изображениями (ImageField) |
| `django-debug-toolbar` | 4.4.6 | Панель отладки |
| `reportlab` | 4.2.5 | Генерация PDF |
| `psycopg2-binary` | (закомментирован) | Драйвер PostgreSQL |

### Команды для работы с requirements.txt:

**Установка всех зависимостей:**
```bash
pip install -r requirements.txt
```

**Создание/обновление файла:**
```bash
# Все установленные пакеты
pip freeze > requirements.txt

# Только пакеты проекта (рекомендуется)
pip list --format=freeze > requirements.txt
```

**Установка в виртуальное окружение:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Best Practices:

1. **Указывайте конкретные версии** (==) для продакшна
2. **Используйте виртуальное окружение** для изоляции зависимостей
3. **Регулярно обновляйте** файл при добавлении пакетов
4. **Комментируйте** опциональные зависимости
5. **Разделяйте** на dev и prod requirements при необходимости

---

## Использование метода save() в модели

### Что это?
Переопределение метода `save()` в модели позволяет добавить кастомную логику при сохранении объекта в БД.

### Назначение:
- Автоматическое заполнение полей
- Валидация перед сохранением
- Обновление связанных объектов
- Логирование изменений
- Вычисление значений

### Примеры в проекте:

#### Пример 1: ReagentMovement - Автоматическое обновление остатка реагента

```194:213:intranet/models.py
def save(self, *args, **kwargs):
    """
    Переопределенный save() с использованием F-выражений
    для автоматического обновления остатка реагента
    """
    is_new = self.pk is None
    super().save(*args, **kwargs)
    
    if is_new:
        # Используем F-выражения для атомарного обновления
        if self.movement_type == 'in':
            Reagent.objects.filter(pk=self.reagent.pk).update(
                on_hand=F('on_hand') + self.quantity
            )
        elif self.movement_type == 'out':
            Reagent.objects.filter(pk=self.reagent.pk).update(
                on_hand=F('on_hand') - self.quantity
            )
        # Перезагружаем объект для обновления значения
        self.reagent.refresh_from_db()
```

**Ключевые моменты:**
1. **`is_new = self.pk is None`** - проверка, новый ли объект
2. **`super().save(*args, **kwargs)`** - вызов родительского метода
3. **`F('on_hand')`** - атомарное обновление в БД (без race conditions)
4. **`refresh_from_db()`** - перезагрузка объекта из БД

### Модель с этим save():

```150:214:intranet/models.py
class ReagentMovement(models.Model):
    """
    Модель движения реагентов (приход/расход)
    Демонстрирует использование F-выражений
    """
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
    date = models.DateTimeField('Дата', default=timezone.now)
    comment = models.TextField('Комментарий', blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reagent_movements',
        verbose_name='Пользователь'
    )
    
    class Meta:
        verbose_name = 'Движение реагента'
        verbose_name_plural = 'Движения реагентов'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_movement_type_display()}: {self.reagent.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        """
        Переопределенный save() с использованием F-выражений
        для автоматического обновления остатка реагента
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Используем F-выражения для атомарного обновления
            if self.movement_type == 'in':
                Reagent.objects.filter(pk=self.reagent.pk).update(
                    on_hand=F('on_hand') + self.quantity
                )
            elif self.movement_type == 'out':
                Reagent.objects.filter(pk=self.reagent.pk).update(
                    on_hand=F('on_hand') - self.quantity
                )
            # Перезагружаем объект для обновления значения
            self.reagent.refresh_from_db()
```

### Типичные паттерны использования save():

```python
# 1. Автоматическое заполнение slug
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.title)
    super().save(*args, **kwargs)

# 2. Установка даты изменения
def save(self, *args, **kwargs):
    self.modified_at = timezone.now()
    super().save(*args, **kwargs)

# 3. Валидация перед сохранением
def save(self, *args, **kwargs):
    if self.start_date > self.end_date:
        raise ValueError("Дата начала не может быть позже даты окончания")
    super().save(*args, **kwargs)

# 4. Обработка изображений
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    if self.image:
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
```

### Важные правила:

1. **Всегда вызывайте `super().save()`** - иначе объект не сохранится в БД
2. **Используйте `*args, **kwargs`** - для поддержки всех параметров
3. **Проверяйте `self.pk`** - чтобы различать создание и обновление
4. **Будьте осторожны с циклами** - не вызывайте save() в save()
5. **Используйте F-выражения** для атомарных операций

---

## Meta widgets в формах

### Что это?
`widgets` в классе `Meta` формы определяют HTML-элементы для отображения полей и их атрибуты.

### Назначение:
- Кастомизация HTML-вывода полей
- Добавление CSS-классов
- Настройка атрибутов (placeholder, type, step)
- Улучшение UX

### Примеры в проекте:

#### Пример 1: ReagentForm - Полный набор виджетов

```85:115:intranet/forms.py
class Meta:
    model = Reagent
    fields = [
        'name', 'category', 'on_hand', 'min_threshold',
        'expiry_date', 'image', 'certificate', 'external_link'
    ]
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

#### Пример 2: TaskForm - Виджеты для разных типов полей

```312:329:intranet/forms.py
widgets = {
    'title': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Краткое описание задачи'
    }),
    'description': forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 5,
        'placeholder': 'Подробное описание задачи'
    }),
    'assignee': forms.Select(attrs={'class': 'form-select'}),
    'status': forms.Select(attrs={'class': 'form-select'}),
    'priority': forms.Select(attrs={'class': 'form-select'}),
    'deadline': forms.DateTimeInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local'
    }),
}
```

#### Пример 3: CultureForm - Виджеты с datetime и select

```254:271:intranet/forms.py
widgets = {
    'name': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Название культуры'
    }),
    'status': forms.Select(attrs={'class': 'form-select'}),
    'seeding_date': forms.DateTimeInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local'
    }),
    'passage_number': forms.NumberInput(attrs={'class': 'form-control'}),
    'recipe': forms.Select(attrs={'class': 'form-select'}),
    'responsible': forms.Select(attrs={'class': 'form-select'}),
    'notes': forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3
    }),
}
```

#### Пример 4: CalendarEventForm - SelectMultiple виджет

```425:447:intranet/forms.py
widgets = {
    'subject': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Тема события'
    }),
    'description': forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3
    }),
    'start_datetime': forms.DateTimeInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local'
    }),
    'end_datetime': forms.DateTimeInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local'
    }),
    'participants': forms.SelectMultiple(attrs={'class': 'form-select'}),
    'location': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Место проведения'
    }),
}
```

#### Пример 5: AnnouncementForm - CheckboxInput

```391:402:intranet/forms.py
widgets = {
    'title': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Заголовок объявления'
    }),
    'text': forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 6,
        'placeholder': 'Текст объявления'
    }),
    'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
}
```

### Типы виджетов Django:

| Виджет | Поле модели | HTML элемент |
|--------|-------------|--------------|
| `TextInput` | CharField | `<input type="text">` |
| `Textarea` | TextField | `<textarea>` |
| `NumberInput` | IntegerField, DecimalField | `<input type="number">` |
| `EmailInput` | EmailField | `<input type="email">` |
| `URLInput` | URLField | `<input type="url">` |
| `DateInput` | DateField | `<input type="date">` |
| `DateTimeInput` | DateTimeField | `<input type="datetime-local">` |
| `TimeInput` | TimeField | `<input type="time">` |
| `CheckboxInput` | BooleanField | `<input type="checkbox">` |
| `Select` | ForeignKey, choices | `<select>` |
| `SelectMultiple` | ManyToManyField | `<select multiple>` |
| `FileInput` | FileField, ImageField | `<input type="file">` |
| `PasswordInput` | CharField | `<input type="password">` |
| `HiddenInput` | Любое поле | `<input type="hidden">` |

### Полезные атрибуты виджетов:

```python
widgets = {
    'field_name': forms.TextInput(attrs={
        'class': 'my-class',           # CSS класс
        'id': 'custom-id',             # HTML ID
        'placeholder': 'Введите...',    # Подсказка
        'required': True,               # Обязательное поле
        'disabled': False,              # Отключить поле
        'readonly': False,              # Только чтение
        'maxlength': 100,              # Макс. длина
        'min': 0,                       # Мин. значение (для number)
        'max': 100,                     # Макс. значение (для number)
        'step': 0.01,                   # Шаг (для number)
        'rows': 5,                      # Строки (для textarea)
        'cols': 40,                     # Столбцы (для textarea)
        'autocomplete': 'off',          # Автозаполнение
        'data-*': 'value',             # Data-атрибуты
    })
}
```

---

## Пример clean_<fieldname>()

### Что это?
Метод `clean_<fieldname>()` в форме выполняет валидацию конкретного поля и возвращает очищенное значение.

### Назначение:
- Кастомная валидация полей
- Преобразование данных
- Проверка бизнес-логики
- Вывод понятных сообщений об ошибках

### Примеры в проекте:

#### Пример 1: ReagentForm - Валидация срока годности

```141:150:intranet/forms.py
def clean_expiry_date(self):
    """
    Валидация срока годности - не должен быть в прошлом
    """
    expiry_date = self.cleaned_data.get('expiry_date')
    if expiry_date and expiry_date < timezone.now().date():
        raise forms.ValidationError(
            'Срок годности не может быть в прошлом'
        )
    return expiry_date
```

**Логика:**
1. Получаем значение из `cleaned_data`
2. Проверяем условие (дата не в прошлом)
3. Если ошибка - поднимаем `ValidationError`
4. Возвращаем очищенное значение

#### Пример 2: ReagentForm - Валидация остатка

```152:161:intranet/forms.py
def clean_on_hand(self):
    """
    Валидация остатка - не может быть отрицательным
    """
    on_hand = self.cleaned_data.get('on_hand')
    if on_hand < 0:
        raise forms.ValidationError(
            'Остаток не может быть отрицательным'
        )
    return on_hand
```

#### Пример 3: TaskForm - Валидация дедлайна

```331:340:intranet/forms.py
def clean_deadline(self):
    """
    Валидация дедлайна - не должен быть в прошлом
    """
    deadline = self.cleaned_data.get('deadline')
    if deadline and deadline < timezone.now():
        raise forms.ValidationError(
            'Дедлайн не может быть в прошлом'
        )
    return deadline
```

### Полная форма с clean методами:

```79:162:intranet/forms.py
class ReagentForm(forms.ModelForm):
    """
    Форма для создания/редактирования реагента
    Демонстрация использования widgets, labels, help_texts, error_messages
    """
    
    class Meta:
        model = Reagent
        fields = [
            'name', 'category', 'on_hand', 'min_threshold',
            'expiry_date', 'image', 'certificate', 'external_link'
        ]
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
        help_texts = {
            'on_hand': 'Текущее количество на складе',
            'min_threshold': 'При достижении этого значения реагент считается критичным',
            'expiry_date': 'Дата окончания срока годности',
        }
        error_messages = {
            'name': {
                'required': 'Пожалуйста, укажите название реагента',
                'max_length': 'Название слишком длинное',
            },
            'category': {
                'required': 'Выберите категорию реагента',
            },
        }
    
    def clean_expiry_date(self):
        """
        Валидация срока годности - не должен быть в прошлом
        """
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date < timezone.now().date():
            raise forms.ValidationError(
                'Срок годности не может быть в прошлом'
            )
        return expiry_date
    
    def clean_on_hand(self):
        """
        Валидация остатка - не может быть отрицательным
        """
        on_hand = self.cleaned_data.get('on_hand')
        if on_hand < 0:
            raise forms.ValidationError(
                'Остаток не может быть отрицательным'
            )
        return on_hand
```

### Дополнительные примеры clean методов:

```python
# 1. Приведение к верхнему регистру
def clean_code(self):
    code = self.cleaned_data.get('code')
    return code.upper() if code else code

# 2. Проверка уникальности
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError('Этот email уже используется')
    return email

# 3. Валидация диапазона
def clean_age(self):
    age = self.cleaned_data.get('age')
    if age < 18 or age > 100:
        raise forms.ValidationError('Возраст должен быть от 18 до 100')
    return age

# 4. Валидация формата
def clean_phone(self):
    phone = self.cleaned_data.get('phone')
    import re
    if not re.match(r'^\+7\d{10}$', phone):
        raise forms.ValidationError('Неверный формат телефона (+7XXXXXXXXXX)')
    return phone

# 5. Множественные проверки
def clean_password(self):
    password = self.cleaned_data.get('password')
    if len(password) < 8:
        raise forms.ValidationError('Пароль должен содержать минимум 8 символов')
    if not any(char.isdigit() for char in password):
        raise forms.ValidationError('Пароль должен содержать хотя бы одну цифру')
    if not any(char.isupper() for char in password):
        raise forms.ValidationError('Пароль должен содержать заглавную букву')
    return password
```

### Метод clean() для валидации нескольких полей:

```python
def clean(self):
    """
    Валидация нескольких полей одновременно
    """
    cleaned_data = super().clean()
    start_date = cleaned_data.get('start_date')
    end_date = cleaned_data.get('end_date')
    
    if start_date and end_date and start_date > end_date:
        raise forms.ValidationError(
            'Дата начала не может быть позже даты окончания'
        )
    
    return cleaned_data
```

---

## def save с commit=True

### Что это?
Параметр `commit` в методе `save()` формы определяет, будет ли объект сразу сохранен в БД или только создан в памяти.

### Назначение:
- Отложенное сохранение в БД
- Установка дополнительных полей перед сохранением
- Работа с ManyToMany полями
- Обработка связанных объектов

### Примеры в проекте:

#### Пример 1: TaskForm - Кастомный save() с commit

```342:356:intranet/forms.py
def save(self, commit=True):
    """
    Кастомный метод save() для автоматической установки создателя
    """
    task = super().save(commit=False)
    
    # Если задача новая и у неё нет создателя, устанавливаем из контекста
    if not task.pk and not task.creator:
        # Создатель будет установлен во view
        pass
    
    if commit:
        task.save()
    
    return task
```

**Логика:**
1. `super().save(commit=False)` - создаем объект без сохранения в БД
2. Модифицируем объект (добавляем поля, проверяем условия)
3. Если `commit=True`, сохраняем в БД
4. Возвращаем объект

#### Пример 2: Использование в view для создания реагента

```253:258:intranet/views.py
if request.method == 'POST':
    form = ReagentForm(request.POST, request.FILES)
    if form.is_valid():
        reagent = form.save()
        messages.success(request, f'Реагент "{reagent.name}" успешно создан')
        return HttpResponseRedirect(reagent.get_absolute_url())
```

#### Пример 3: Использование в view для редактирования

```286:291:intranet/views.py
if request.method == 'POST':
    form = ReagentForm(request.POST, request.FILES, instance=reagent)
    if form.is_valid():
        updated_reagent = form.save(commit=True)
        messages.success(request, f'Реагент "{updated_reagent.name}" обновлен')
        return HttpResponseRedirect(updated_reagent.get_absolute_url())
```

#### Пример 4: Использование в view для загрузки документа

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
*Здесь `commit=False` используется для установки поля `uploaded_by` перед сохранением.*

### Детальный пример с ManyToMany:

```python
class RecipeCreateView(View):
    def post(self, request):
        form = RecipeForm(request.POST)
        if form.is_valid():
            # Сохраняем без commit, чтобы добавить автора
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            # ВАЖНО: для ManyToMany нужно вызвать save_m2m()
            # после сохранения основного объекта
            form.save_m2m()
            
            return redirect('recipe_detail', pk=recipe.pk)
```

### Типичные паттерны использования:

```python
# 1. Установка пользователя
def post(self, request):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.creator = request.user
        task.save()
        return redirect('task_list')

# 2. Установка нескольких полей
def post(self, request):
    form = AnnouncementForm(request.POST)
    if form.is_valid():
        announcement = form.save(commit=False)
        announcement.author = request.user
        announcement.published_at = timezone.now()
        announcement.save()
        return redirect('announcements')

# 3. Обработка перед сохранением
def post(self, request):
    form = ReagentForm(request.POST, request.FILES)
    if form.is_valid():
        reagent = form.save(commit=False)
        # Обработка изображения
        if reagent.image:
            reagent.image = process_image(reagent.image)
        reagent.save()
        return redirect('reagent_detail', pk=reagent.pk)

# 4. Работа с транзакциями
from django.db import transaction

def post(self, request):
    form = RecipeForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()
            
            # Создание связанных объектов
            for reagent_id in request.POST.getlist('reagents'):
                RecipeReagent.objects.create(
                    recipe=recipe,
                    reagent_id=reagent_id,
                    quantity=1.0
                )
        
        return redirect('recipe_detail', pk=recipe.pk)
```

### Важные моменты:

1. **`commit=False`** - объект создается, но не сохраняется в БД
2. **`commit=True`** (по умолчанию) - объект сразу сохраняется в БД
3. **ManyToMany** - после `commit=False` нужно вызвать `save_m2m()`
4. **Связанные объекты** - требуют сохраненного основного объекта (с pk)
5. **Транзакции** - используйте `transaction.atomic()` для целостности данных

---

## models.ManyToManyField с параметром through

### Что это?
Параметр `through` в `ManyToManyField` позволяет указать кастомную промежуточную модель для связи многие-ко-многим с дополнительными полями.

### Назначение:
- Добавление дополнительных данных к связи
- Сложные отношения между моделями
- Хранение метаданных связи
- Более гибкое управление связями

### Пример в проекте:

#### Модель Recipe с through='RecipeReagent'

```220:265:intranet/models.py
class Recipe(models.Model):
    """
    Модель рецептуры (протокола)
    """
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('approved', 'Утверждён'),
        ('archived', 'Архивный'),
    ]
    
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    reagents = models.ManyToManyField(
        Reagent,
        through='RecipeReagent',
        related_name='used_in_recipes',
        verbose_name='Реагенты'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    approved_at = models.DateTimeField('Дата утверждения', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Рецептура'
        verbose_name_plural = 'Рецептуры'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.pk})
```

**Ключевое поле:**
```245:249:intranet/models.py
reagents = models.ManyToManyField(
    Reagent,
    through='RecipeReagent',
    related_name='used_in_recipes',
    verbose_name='Реагенты'
)
```

#### Промежуточная модель RecipeReagent

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

**Дополнительные поля связи:**
- `quantity` - количество реагента
- `unit` - единица измерения

### Форма для промежуточной модели:

```221:236:intranet/forms.py
class RecipeReagentForm(forms.ModelForm):
    """
    Форма для добавления реагента в рецептуру
    """
    
    class Meta:
        model = RecipeReagent
        fields = ['reagent', 'quantity', 'unit']
        widgets = {
            'reagent': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'unit': forms.Select(attrs={'class': 'form-select'}),
        }
```

### Использование through модели:

```python
# 1. Создание связи с дополнительными данными
recipe = Recipe.objects.get(pk=1)
reagent = Reagent.objects.get(pk=5)

# Через промежуточную модель
RecipeReagent.objects.create(
    recipe=recipe,
    reagent=reagent,
    quantity=100.0,
    unit='ml'
)

# 2. Получение всех реагентов рецептуры
recipe_reagents = recipe.reagents.all()

# 3. Получение данных с дополнительными полями
for rr in recipe.recipeреагент_set.all():
    print(f"{rr.reagent.name}: {rr.quantity} {rr.get_unit_display()}")

# 4. Фильтрация по промежуточной модели
recipes_with_enzyme = Recipe.objects.filter(
    recipeреагент__reagent__category='enzyme'
).distinct()

# 5. Обновление количества
rr = RecipeReagent.objects.get(recipe=recipe, reagent=reagent)
rr.quantity = 150.0
rr.save()

# 6. Удаление связи
RecipeReagent.objects.filter(recipe=recipe, reagent=reagent).delete()
```

### Сравнение: с through vs без through

**Без through (простая связь):**
```python
class Recipe(models.Model):
    reagents = models.ManyToManyField(Reagent)

# Использование
recipe.reagents.add(reagent)  # Просто добавление
recipe.reagents.remove(reagent)
```

**С through (с дополнительными данными):**
```python
class Recipe(models.Model):
    reagents = models.ManyToManyField(Reagent, through='RecipeReagent')

# Использование
RecipeReagent.objects.create(
    recipe=recipe,
    reagent=reagent,
    quantity=100.0,
    unit='ml'
)

# НЕЛЬЗЯ использовать add(), remove(), clear() напрямую!
# recipe.reagents.add(reagent)  # Вызовет ошибку!
```

### Преимущества through:
1. **Дополнительные данные** - количество, дата, комментарий и т.д.
2. **Более точная модель** - отражает реальные отношения
3. **Сложные запросы** - фильтрация по данным связи
4. **Аудит** - можно добавить created_at, updated_at к связи
5. **Валидация** - проверка данных на уровне модели

---

## select_related()

### Что это?
`select_related()` - это оптимизация запросов для ForeignKey и OneToOne полей через SQL JOIN. Загружает связанные объекты за один запрос.

### Назначение:
- Уменьшение количества запросов к БД (решает проблему N+1)
- Оптимизация производительности
- Загрузка связанных объектов за один SELECT с JOIN
- Работает только с ForeignKey и OneToOne

### Примеры в проекте:

#### Пример 1: Загрузка объявлений с авторами

```82:84:intranet/views.py
latest_announcements = Announcement.objects.select_related('author').order_by(
    '-is_pinned', '-published_at'
)[:5]
```

**Без select_related:**
```sql
-- 1 запрос для объявлений
SELECT * FROM announcement ORDER BY is_pinned DESC, published_at DESC LIMIT 5;
-- + 5 запросов для авторов (N+1 проблема!)
SELECT * FROM user WHERE id = 1;
SELECT * FROM user WHERE id = 2;
...
```

**С select_related:**
```sql
-- Один запрос с JOIN
SELECT announcement.*, user.* 
FROM announcement 
LEFT JOIN user ON announcement.author_id = user.id
ORDER BY is_pinned DESC, published_at DESC 
LIMIT 5;
```

#### Пример 2: Загрузка задач с исполнителем и создателем

```87:91:intranet/views.py
user_tasks = Task.objects.filter(
    assignee=request.user
).exclude(
    status='done'
).select_related('creator').order_by('deadline', '-priority')[:5]
```

#### Пример 3: Множественные select_related

```345:345:intranet/views.py
tasks = Task.objects.all().select_related('assignee', 'creator')
```
*Загружает задачи вместе с исполнителем И создателем за один запрос.*

#### Пример 4: Загрузка рецептов с автором

```220:220:intranet/views.py
recipes = reagent.used_in_recipes.all().select_related('author')
```

#### Пример 5: Загрузка документов с загрузчиком

```528:528:intranet/views.py
documents = DocumentTemplate.objects.all().select_related('uploaded_by').order_by('-uploaded_at')
```

#### Пример 6: Загрузка культур с ответственным и рецептом

```550:552:intranet/views.py
cultures = Culture.objects.all().select_related(
    'responsible', 'recipe'
).prefetch_related('events')
```

#### Пример 7: Загрузка объявлений с автором (список)

```604:606:intranet/views.py
announcements = Announcement.objects.all().select_related('author').order_by(
    '-is_pinned', '-published_at'
)
```

### Визуализация работы select_related:

```python
# БЕЗ select_related (плохо - N+1 запросов)
tasks = Task.objects.all()  # 1 запрос
for task in tasks:
    print(task.assignee.username)  # +1 запрос для каждой итерации!

# С select_related (хорошо - 1 запрос)
tasks = Task.objects.select_related('assignee')  # 1 запрос с JOIN
for task in tasks:
    print(task.assignee.username)  # Без дополнительных запросов!
```

### Вложенные select_related (через связи):

```python
# Загрузка через несколько уровней связей
movements = ReagentMovement.objects.select_related(
    'reagent',              # Реагент движения
    'user__role',           # Пользователь и его роль
    'reagent__category'     # Категория реагента
)

# Теперь можно без дополнительных запросов:
for movement in movements:
    print(movement.reagent.name)
    print(movement.user.role)
    print(movement.reagent.category)
```

### Когда использовать select_related:

✅ **Используйте для:**
- ForeignKey полей
- OneToOne полей
- Связей, которые точно будут использоваться
- Списков объектов (list views)

❌ **НЕ используйте для:**
- ManyToMany полей (используйте `prefetch_related`)
- Обратных ForeignKey (reverse) - используйте `prefetch_related`
- Когда связанные объекты не нужны

### Производительность:

```python
# Пример измерения
from django.db import connection
from django.test.utils import override_settings

# БЕЗ select_related
with override_settings(DEBUG=True):
    connection.queries = []
    tasks = Task.objects.all()
    for task in tasks:
        _ = task.assignee.username
    print(f"Запросов: {len(connection.queries)}")  # 101 (если 100 задач)

# С select_related
with override_settings(DEBUG=True):
    connection.queries = []
    tasks = Task.objects.select_related('assignee')
    for task in tasks:
        _ = task.assignee.username
    print(f"Запросов: {len(connection.queries)}")  # 1
```

---

## prefetch_related()

### Что это?
`prefetch_related()` - это оптимизация для ManyToMany и обратных ForeignKey. Выполняет отдельные запросы для каждой таблицы и объединяет результаты в Python.

### Назначение:
- Оптимизация ManyToMany полей
- Оптимизация обратных ForeignKey (reverse relations)
- Уменьшение N+1 проблемы
- Работа со сложными связями

### Примеры в проекте:

#### Пример 1: Загрузка реагента с движениями и пользователями

```211:213:intranet/views.py
reagent = get_object_or_404(
    Reagent.objects.prefetch_related('movements__user'),
    pk=pk
)
```

**Запросы:**
```sql
-- 1. Получение реагента
SELECT * FROM reagent WHERE id = ?;

-- 2. Получение всех движений этого реагента
SELECT * FROM reagent_movement WHERE reagent_id = ?;

-- 3. Получение пользователей этих движений
SELECT * FROM user WHERE id IN (1, 2, 3, ...);
```
*Всего 3 запроса вместо N+1!*

#### Пример 2: Загрузка культур с событиями

```550:552:intranet/views.py
cultures = Culture.objects.all().select_related(
    'responsible', 'recipe'
).prefetch_related('events')
```
*Комбинация `select_related` для ForeignKey и `prefetch_related` для обратной связи.*

#### Пример 3: Загрузка рецептов с реагентами

```578:578:intranet/views.py
recipes = Recipe.objects.all().select_related('author').prefetch_related('reagents')
```

### Разница между select_related и prefetch_related:

| Критерий | select_related | prefetch_related |
|----------|----------------|------------------|
| **Тип связи** | ForeignKey, OneToOne | ManyToMany, обратные ForeignKey |
| **Метод** | SQL JOIN | Отдельные SELECT |
| **Запросы** | 1 запрос | N запросов (где N - кол-во таблиц) |
| **Когда использовать** | Когда нужен один связанный объект | Когда нужно много связанных объектов |

### Визуальное сравнение:

```python
# select_related - для ForeignKey (один объект)
task = Task.objects.select_related('assignee').get(pk=1)
print(task.assignee.username)  # Без доп. запросов

# prefetch_related - для обратной связи (много объектов)
reagent = Reagent.objects.prefetch_related('movements').get(pk=1)
for movement in reagent.movements.all():  # Без доп. запросов
    print(movement.quantity)
```

### Сложные prefetch с вложенными связями:

```python
# Загрузка реагентов с движениями и пользователями движений
reagents = Reagent.objects.prefetch_related(
    'movements',              # Движения реагента
    'movements__user',        # Пользователи движений
    'used_in_recipes',        # Рецептуры, где используется
    'used_in_recipes__author' # Авторы рецептур
)

for reagent in reagents:
    print(f"Реагент: {reagent.name}")
    for movement in reagent.movements.all():
        print(f"  Движение: {movement.quantity} от {movement.user.username}")
    for recipe in reagent.used_in_recipes.all():
        print(f"  Рецепт: {recipe.name} (автор: {recipe.author.username})")
```

### Prefetch с фильтрацией (Prefetch object):

```python
from django.db.models import Prefetch

# Только последние 5 движений
reagents = Reagent.objects.prefetch_related(
    Prefetch(
        'movements',
        queryset=ReagentMovement.objects.order_by('-date')[:5],
        to_attr='recent_movements'
    )
)

for reagent in reagents:
    for movement in reagent.recent_movements:  # Используем to_attr
        print(movement)
```

### Комбинация select_related и prefetch_related:

```python
# Оптимальная загрузка задач
tasks = Task.objects.select_related(
    'assignee',      # ForeignKey - используем select_related
    'creator'        # ForeignKey - используем select_related
).prefetch_related(
    'comments',      # Обратная связь - используем prefetch_related
    'comments__user' # И пользователи комментариев
)

for task in tasks:
    print(f"Задача: {task.title}")
    print(f"Исполнитель: {task.assignee.username}")
    print(f"Создатель: {task.creator.username}")
    print("Комментарии:")
    for comment in task.comments.all():
        print(f"  {comment.user.username}: {comment.text}")
```

### Производительность:

```python
# БЕЗ prefetch_related
reagents = Reagent.objects.all()  # 1 запрос
for reagent in reagents:
    for movement in reagent.movements.all():  # +1 запрос на каждый реагент!
        print(movement)
# Итого: 1 + N запросов (если 100 реагентов = 101 запрос)

# С prefetch_related
reagents = Reagent.objects.prefetch_related('movements')  # 2 запроса
for reagent in reagents:
    for movement in reagent.movements.all():  # Без доп. запросов
        print(movement)
# Итого: 2 запроса (независимо от количества реагентов)
```

### Когда использовать:

✅ **prefetch_related для:**
- ManyToManyField
- Обратных ForeignKey (`related_name`)
- GenericRelation
- Когда нужно много связанных объектов

✅ **select_related для:**
- ForeignKey
- OneToOneField
- Когда нужен один связанный объект

---

## django-debug-toolbar

### Что это?
`django-debug-toolbar` - это панель отладки для Django, показывающая детальную информацию о запросах, производительности, шаблонах и многом другом.

### Назначение:
- Мониторинг SQL-запросов
- Анализ производительности
- Отладка шаблонов
- Просмотр контекста
- Профилирование кода

### Установка в проекте:

#### 1. Зависимость в requirements.txt

```4:4:requirements.txt
django-debug-toolbar==4.4.6
```

#### 2. Установка:
```bash
pip install -r requirements.txt
```

#### 3. Настройка в INSTALLED_APPS

```31:45:ddc_intranet/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Наше приложение
    'intranet',
    
    # Сторонние приложения
    'rest_framework',
    'debug_toolbar',
]
```

#### 4. Добавление middleware

```47:58:ddc_intranet/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Debug toolbar (только для DEBUG=True)
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
```

#### 5. Настройка INTERNAL_IPS

```174:178:ddc_intranet/settings.py
# Django Debug Toolbar Configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]
```

#### 6. Подключение URLs

Нужно добавить в основной `urls.py`:

```python
# ddc_intranet/urls.py
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    # ... другие URL
]

# Добавляем Debug Toolbar только для DEBUG=True
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
```

### Панели Debug Toolbar:

#### 1. **SQL панель** (самая важная!)
- Показывает все SQL-запросы
- Время выполнения каждого запроса
- Повторяющиеся запросы (highlight duplicate queries)
- EXPLAIN для каждого запроса

**Пример использования:**
```python
# Проблемный код
tasks = Task.objects.all()
for task in tasks:
    print(task.assignee.username)  # N+1 запросов!

# Debug Toolbar покажет 101 запрос

# Оптимизированный код
tasks = Task.objects.select_related('assignee')
for task in tasks:
    print(task.assignee.username)

# Debug Toolbar покажет 1 запрос
```

#### 2. **Timer панель**
- Общее время выполнения
- Время на рендеринг шаблона
- Время на выполнение SQL
- CPU time

#### 3. **Templates панель**
- Показывает используемые шаблоны
- Контекст каждого шаблона
- Порядок наследования шаблонов
- Template context processors

#### 4. **Cache панель**
- Обращения к кэшу
- Cache hits/misses
- Ключи кэша

#### 5. **Signals панель**
- Django сигналы
- Время выполнения обработчиков

#### 6. **Logging панель**
- Логи приложения
- Уровни логирования
- Сообщения

### Практическое использование:

#### Поиск проблем N+1:

```python
# В view
@login_required
def task_list(request):
    # ПЛОХО - будет много запросов
    tasks = Task.objects.all()
    
    # Debug Toolbar покажет:
    # 1 запрос для задач + N запросов для пользователей
    
    return render(request, 'task_list.html', {'tasks': tasks})

# В шаблоне
{% for task in tasks %}
    {{ task.title }} - {{ task.assignee.username }}
    {# Здесь происходит дополнительный запрос! #}
{% endfor %}
```

**Решение:**
```python
@login_required
def task_list(request):
    # ХОРОШО - один запрос с JOIN
    tasks = Task.objects.select_related('assignee', 'creator')
    
    # Debug Toolbar покажет: 1 запрос
    
    return render(request, 'task_list.html', {'tasks': tasks})
```

### Дополнительные настройки:

```python
# settings.py

# Показывать только в DEBUG режиме
DEBUG = True

# Настройка панелей
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# Дополнительные настройки
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'INTERCEPT_REDIRECTS': False,  # Не перехватывать редиректы
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
}
```

### Команды для анализа:

```python
# Включить SQL логирование в консоль
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Best Practices:

1. **Используйте только в разработке** - отключайте в продакшне
2. **Проверяйте количество запросов** - стремитесь к минимуму
3. **Используйте select_related/prefetch_related** - для оптимизации
4. **Анализируйте медленные запросы** - оптимизируйте через индексы
5. **Проверяйте дубликаты** - Debug Toolbar их подсвечивает

---

## Итоговая шпаргалка

| Тема | Файл | Строки | Ключевые концепции |
|------|------|--------|-------------------|
| **ModelForm** | `forms.py` | 79-162, 300-356 | Meta, fields, widgets |
| **requirements.txt** | `requirements.txt` | 1-10 | Django, DRF, Pillow, debug-toolbar |
| **save() в модели** | `models.py` | 194-213 | F-выражения, атомарность |
| **Meta widgets** | `forms.py` | 91-115, 312-329 | TextInput, Select, DateInput |
| **clean_fieldname** | `forms.py` | 141-150, 152-161 | ValidationError, cleaned_data |
| **save(commit)** | `forms.py`, `views.py` | 342-356, 505-512 | commit=False, save_m2m() |
| **ManyToMany through** | `models.py` | 245-249, 267-308 | RecipeReagent, quantity, unit |
| **select_related** | `views.py` | 82-84, 345, 528 | ForeignKey, JOIN |
| **prefetch_related** | `views.py` | 211-213, 550-552 | ManyToMany, отдельные запросы |
| **debug-toolbar** | `settings.py`, `requirements.txt` | 44, 57, 175-178 | SQL анализ, профилирование |

---

## Контрольные вопросы для защиты

### 1. В чем разница между select_related и prefetch_related?
- **select_related**: SQL JOIN, ForeignKey/OneToOne, 1 запрос
- **prefetch_related**: Отдельные SELECT, ManyToMany/обратные FK, N запросов

### 2. Зачем нужен параметр through в ManyToManyField?
- Для добавления дополнительных полей к связи (quantity, unit, date и т.д.)

### 3. Что возвращает form.save(commit=False)?
- Объект модели, созданный но не сохраненный в БД

### 4. Когда нужно вызывать form.save_m2m()?
- После save(commit=False) для сохранения ManyToMany связей

### 5. Для чего используется clean_<fieldname>()?
- Для кастомной валидации конкретного поля формы

### 6. Как Debug Toolbar помогает оптимизировать запросы?
- Показывает количество и время выполнения SQL запросов, выявляет N+1 проблемы

### 7. Зачем переопределять save() в модели?
- Для добавления логики перед/после сохранения (авто-заполнение, валидация, обновление связанных объектов)

### 8. Что такое виджеты в формах?
- HTML-элементы для отображения полей формы (input, select, textarea и т.д.)

