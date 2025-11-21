"""
Формы для интранета DDC Biotech
Все формы собраны в одном файле
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import (
    User, Reagent, ReagentMovement, Recipe, RecipeReagent,
    Culture, CultureEvent, Task, TaskComment, Announcement,
    CalendarEvent, DocumentTemplate
)


# ============================================================================
# ФОРМЫ АУТЕНТИФИКАЦИИ
# ============================================================================

class UserLoginForm(AuthenticationForm):
    """
    Форма входа в систему
    """
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


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


# ============================================================================
# ФОРМЫ РЕАГЕНТОВ
# ============================================================================

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


class ReagentMovementForm(forms.ModelForm):
    """
    Форма для регистрации движения реагента
    """
    
    class Meta:
        model = ReagentMovement
        fields = ['reagent', 'quantity', 'movement_type', 'comment']
        widgets = {
            'reagent': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


# ============================================================================
# ФОРМЫ РЕЦЕПТУР
# ============================================================================

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


# ============================================================================
# ФОРМЫ КУЛЬТУР
# ============================================================================

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


class CultureEventForm(forms.ModelForm):
    """
    Форма для регистрации события с культурой
    """
    
    class Meta:
        model = CultureEvent
        fields = ['culture', 'event_type', 'date', 'comment']
        widgets = {
            'culture': forms.Select(attrs={'class': 'form-select'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


# ============================================================================
# ФОРМЫ ЗАДАЧ
# ============================================================================

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


class TaskCommentForm(forms.ModelForm):
    """
    Форма для добавления комментария к задаче
    """
    
    class Meta:
        model = TaskComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите комментарий...'
            }),
        }
        labels = {
            'text': 'Комментарий',
        }


# ============================================================================
# ФОРМЫ ОБЪЯВЛЕНИЙ
# ============================================================================

class AnnouncementForm(forms.ModelForm):
    """
    Форма для создания объявления
    """
    
    class Meta:
        model = Announcement
        fields = ['title', 'text', 'is_pinned']
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
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'is_pinned': 'Закрепить вверху',
        }


# ============================================================================
# ФОРМЫ КАЛЕНДАРЯ
# ============================================================================

class CalendarEventForm(forms.ModelForm):
    """
    Форма для создания события календаря
    """
    
    class Meta:
        model = CalendarEvent
        fields = [
            'subject', 'description', 'start_datetime',
            'end_datetime', 'participants', 'location'
        ]
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


# ============================================================================
# ФОРМЫ ДОКУМЕНТОВ
# ============================================================================

class DocumentTemplateForm(forms.ModelForm):
    """
    Форма для загрузки документа
    """
    
    class Meta:
        model = DocumentTemplate
        fields = ['name', 'description', 'file']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название документа'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Краткое описание'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ============================================================================
# ФОРМА ПОИСКА
# ============================================================================

class SearchForm(forms.Form):
    """
    Универсальная форма поиска для дашборда
    """
    q = forms.CharField(
        label='Поиск',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск...',
            'autocomplete': 'off'
        })
    )
    
    search_type = forms.ChoiceField(
        label='Искать в',
        required=False,
        choices=[
            ('all', 'Везде'),
            ('reagents', 'Реагенты'),
            ('tasks', 'Задачи'),
            ('announcements', 'Объявления'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


