"""
Модели для интранета DDC Biotech
Все модели собраны в одном файле для студенческого монолитного проекта
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from django.db.models import F


# ============================================================================
# ПОЛЬЗОВАТЕЛИ И РОЛИ
# ============================================================================

class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями для интранета
    """
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
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    profile_url = models.URLField(
        'Ссылка на профиль',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


# ============================================================================
# РЕАГЕНТЫ И ДВИЖЕНИЯ
# ============================================================================

class ActiveReagentManager(models.Manager):
    """
    Кастомный менеджер для активных реагентов (с остатком больше 0)
    """
    def get_queryset(self):
        return super().get_queryset().filter(on_hand__gt=0)


class Reagent(models.Model):
    """
    Модель реагента/химического вещества
    """
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
    on_hand = models.DecimalField(
        'Остаток',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    min_threshold = models.DecimalField(
        'Минимальный порог',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    expiry_date = models.DateField(
        'Срок годности',
        null=True,
        blank=True
    )
    image = models.ImageField(
        'Изображение',
        upload_to='reagents/',
        blank=True,
        null=True
    )
    certificate = models.FileField(
        'Сертификат',
        upload_to='certificates/',
        blank=True,
        null=True
    )
    external_link = models.URLField(
        'Внешняя ссылка',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    # Менеджеры
    objects = models.Manager()
    active = ActiveReagentManager()
    
    class Meta:
        verbose_name = 'Реагент'
        verbose_name_plural = 'Реагенты'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_absolute_url(self):
        """Возвращает URL для детальной страницы реагента"""
        return reverse('reagent_detail', kwargs={'pk': self.pk})
    
    def is_critical(self):
        """Проверяет, критичен ли остаток реагента"""
        return self.on_hand <= self.min_threshold
    
    def is_expiring_soon(self):
        """Проверяет, истекает ли срок годности в ближайшие 30 дней"""
        if not self.expiry_date:
            return False
        days_left = (self.expiry_date - timezone.now().date()).days
        return 0 <= days_left <= 30


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


# ============================================================================
# РЕЦЕПТУРЫ
# ============================================================================

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


# ============================================================================
# КУЛЬТУРЫ И СОБЫТИЯ
# ============================================================================

class Culture(models.Model):
    """
    Модель культуры (клеточная линия, штамм и т.д.)
    """
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('frozen', 'Замороженная'),
        ('discarded', 'Утилизирована'),
    ]
    
    name = models.CharField('Название', max_length=255)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    seeding_date = models.DateTimeField(
        'Дата посева',
        default=timezone.now
    )
    passage_number = models.IntegerField('Номер пассажа', default=0)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cultures',
        verbose_name='Рецептура среды'
    )
    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_cultures',
        verbose_name='Ответственный'
    )
    notes = models.TextField('Примечания', blank=True)
    
    class Meta:
        verbose_name = 'Культура'
        verbose_name_plural = 'Культуры'
        ordering = ['-seeding_date']
    
    def __str__(self):
        return f"{self.name} (P{self.passage_number})"
    
    def get_absolute_url(self):
        return reverse('culture_detail', kwargs={'pk': self.pk})


class CultureEvent(models.Model):
    """
    События с культурой (пассаж, подкормка, замораживание и т.д.)
    """
    EVENT_CHOICES = [
        ('passage', 'Пассаж'),
        ('feeding', 'Подкормка'),
        ('freezing', 'Замораживание'),
        ('thawing', 'Размораживание'),
        ('observation', 'Наблюдение'),
        ('disposal', 'Утилизация'),
    ]
    
    culture = models.ForeignKey(
        Culture,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Культура'
    )
    event_type = models.CharField(
        'Тип события',
        max_length=20,
        choices=EVENT_CHOICES
    )
    date = models.DateTimeField('Дата и время', default=timezone.now)
    comment = models.TextField('Комментарий', blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='culture_events',
        verbose_name='Пользователь'
    )
    
    class Meta:
        verbose_name = 'События культуры'
        verbose_name_plural = 'События культур'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.culture.name}: {self.get_event_type_display()} ({self.date.strftime('%d.%m.%Y')})"


# ============================================================================
# ЗАДАЧИ И КОММЕНТАРИИ
# ============================================================================

class Task(models.Model):
    """
    Модель задачи для сотрудников
    """
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
    priority = models.CharField(
        'Приоритет',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    deadline = models.DateTimeField('Срок выполнения', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['deadline', '-priority']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})
    
    def is_overdue(self):
        """Проверяет, просрочена ли задача"""
        if not self.deadline:
            return False
        return timezone.now() > self.deadline and self.status != 'done'


class TaskComment(models.Model):
    """
    Комментарии к задачам
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Задача'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_comments',
        verbose_name='Пользователь'
    )
    text = models.TextField('Текст комментария')
    date = models.DateTimeField('Дата', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Комментарий к задаче'
        verbose_name_plural = 'Комментарии к задачам'
        ordering = ['date']
    
    def __str__(self):
        return f"Комментарий к {self.task.title} от {self.user}"


# ============================================================================
# ОБЪЯВЛЕНИЯ, КАЛЕНДАРЬ, ДОКУМЕНТЫ
# ============================================================================

class Announcement(models.Model):
    """
    Объявления для сотрудников
    """
    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements',
        verbose_name='Автор'
    )
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    is_pinned = models.BooleanField('Закреплено', default=False)
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-is_pinned', '-published_at']
    
    def __str__(self):
        return self.title


class CalendarEvent(models.Model):
    """
    События календаря
    """
    subject = models.CharField('Тема', max_length=255)
    description = models.TextField('Описание', blank=True)
    start_datetime = models.DateTimeField('Дата и время начала')
    end_datetime = models.DateTimeField('Дата и время окончания', null=True, blank=True)
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='organized_events',
        verbose_name='Организатор'
    )
    participants = models.ManyToManyField(
        User,
        related_name='calendar_events',
        blank=True,
        verbose_name='Участники'
    )
    location = models.CharField('Место', max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Событие календаря'
        verbose_name_plural = 'События календаря'
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.subject} ({self.start_datetime.strftime('%d.%m.%Y %H:%M')})"


class DocumentTemplate(models.Model):
    """
    Шаблоны документов и документация
    """
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    file = models.FileField(
        'Файл',
        upload_to='documents/'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Загружено пользователем'
    )
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Шаблон документа'
        verbose_name_plural = 'Шаблоны документов'
        ordering = ['name']
    
    def __str__(self):
        return self.name
