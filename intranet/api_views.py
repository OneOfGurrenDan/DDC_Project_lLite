"""
API ViewSets для интранета DDC Biotech
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import (
    User, Reagent, ReagentMovement, Recipe, RecipeReagent,
    Culture, CultureEvent, Task, TaskComment, Announcement,
    CalendarEvent, DocumentTemplate
)
from .serializers import (
    UserSerializer, ReagentSerializer, ReagentMovementSerializer,
    RecipeSerializer, RecipeReagentSerializer, CultureSerializer,
    CultureEventSerializer, TaskSerializer, TaskCommentSerializer,
    AnnouncementSerializer, CalendarEventSerializer, DocumentTemplateSerializer
)


# ============================================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра пользователей
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить данные текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


# ============================================================================
# РЕАГЕНТЫ
# ============================================================================

class ReagentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с реагентами
    Поддерживает CRUD операции
    """
    queryset = Reagent.objects.all()
    serializer_class = ReagentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['name', 'on_hand', 'expiry_date', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Фильтрация реагентов по параметрам запроса
        """
        queryset = super().get_queryset()
        
        # Фильтр по категории
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Фильтр по критичному остатку
        is_critical = self.request.query_params.get('is_critical', None)
        if is_critical == 'true':
            queryset = queryset.filter(on_hand__lte=models.F('min_threshold'))
        
        # Только активные реагенты (с остатком > 0)
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(on_hand__gt=0)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Получить движения конкретного реагента"""
        reagent = self.get_object()
        movements = reagent.movements.all()
        serializer = ReagentMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Получить список реагентов с критичным остатком"""
        critical_reagents = self.queryset.filter(on_hand__lte=models.F('min_threshold'))
        serializer = self.get_serializer(critical_reagents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """Получить список реагентов с истекающим сроком годности"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        month_later = today + timedelta(days=30)
        
        expiring_reagents = self.queryset.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=month_later
        )
        serializer = self.get_serializer(expiring_reagents, many=True)
        return Response(serializer.data)


class ReagentMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с движениями реагентов
    """
    queryset = ReagentMovement.objects.select_related('reagent', 'user').all()
    serializer_class = ReagentMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reagent__name', 'comment']
    ordering_fields = ['date', 'quantity']
    ordering = ['-date']
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


# ============================================================================
# РЕЦЕПТУРЫ
# ============================================================================

class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептурами
    """
    queryset = Recipe.objects.select_related('author').prefetch_related('reagents').all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация рецептур по статусу"""
        queryset = super().get_queryset()
        
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем автора"""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Утвердить рецептуру"""
        from django.utils import timezone
        
        recipe = self.get_object()
        recipe.status = 'approved'
        recipe.approved_at = timezone.now()
        recipe.save()
        
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


# ============================================================================
# КУЛЬТУРЫ
# ============================================================================

class CultureViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с культурами
    """
    queryset = Culture.objects.select_related('recipe', 'responsible').prefetch_related('events').all()
    serializer_class = CultureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'notes']
    ordering_fields = ['name', 'seeding_date', 'passage_number']
    ordering = ['-seeding_date']
    
    def get_queryset(self):
        """Фильтрация культур по статусу"""
        queryset = super().get_queryset()
        
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Получить все события конкретной культуры"""
        culture = self.get_object()
        events = culture.events.all()
        serializer = CultureEventSerializer(events, many=True)
        return Response(serializer.data)


class CultureEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с событиями культур
    """
    queryset = CultureEvent.objects.select_related('culture', 'user').all()
    serializer_class = CultureEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['culture__name', 'comment']
    ordering_fields = ['date', 'event_type']
    ordering = ['-date']
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


# ============================================================================
# ЗАДАЧИ
# ============================================================================

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с задачами
    """
    queryset = Task.objects.select_related('assignee', 'creator').prefetch_related('comments').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority', 'status']
    ordering = ['deadline', '-priority']
    
    def get_queryset(self):
        """Фильтрация задач"""
        queryset = super().get_queryset()
        
        # Фильтр по статусу
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Фильтр по приоритету
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Мои задачи (где я исполнитель)
        my_tasks = self.request.query_params.get('my_tasks', None)
        if my_tasks == 'true':
            queryset = queryset.filter(assignee=self.request.user)
        
        # Созданные мной задачи
        created_by_me = self.request.query_params.get('created_by_me', None)
        if created_by_me == 'true':
            queryset = queryset.filter(creator=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем создателя"""
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменить статус задачи"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Неверный статус'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Получить просроченные задачи"""
        from django.utils import timezone
        
        overdue_tasks = self.queryset.filter(
            deadline__lt=timezone.now(),
            status__in=['new', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с комментариями к задачам
    """
    queryset = TaskComment.objects.select_related('task', 'user').all()
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text']
    ordering_fields = ['date']
    ordering = ['date']
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


# ============================================================================
# ОБЪЯВЛЕНИЯ И КАЛЕНДАРЬ
# ============================================================================

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с объявлениями
    """
    queryset = Announcement.objects.select_related('author').all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text']
    ordering_fields = ['published_at', 'is_pinned']
    ordering = ['-is_pinned', '-published_at']
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем автора"""
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Получить закрепленные объявления"""
        pinned = self.queryset.filter(is_pinned=True)
        serializer = self.get_serializer(pinned, many=True)
        return Response(serializer.data)


class CalendarEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с событиями календаря
    """
    queryset = CalendarEvent.objects.select_related('organizer').prefetch_related('participants').all()
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'description', 'location']
    ordering_fields = ['start_datetime', 'end_datetime']
    ordering = ['start_datetime']
    
    def get_queryset(self):
        """Фильтрация событий по датам"""
        queryset = super().get_queryset()
        
        # Фильтр по дате начала
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(start_datetime__gte=start_date)
        
        # Фильтр по дате окончания
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(start_datetime__lte=end_date)
        
        # Мои события
        my_events = self.request.query_params.get('my_events', None)
        if my_events == 'true':
            queryset = queryset.filter(
                Q(organizer=self.request.user) | Q(participants=self.request.user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем организатора"""
        serializer.save(organizer=self.request.user)


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с документами
    """
    queryset = DocumentTemplate.objects.select_related('uploaded_by').all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'uploaded_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем загрузившего пользователя"""
        serializer.save(uploaded_by=self.request.user)


