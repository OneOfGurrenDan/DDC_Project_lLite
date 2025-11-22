"""
Сериализаторы для REST API интранета DDC Biotech
"""

from rest_framework import serializers
from .models import (
    User, Reagent, ReagentMovement, Recipe, RecipeReagent,
    Culture, CultureEvent, Task, TaskComment, Announcement,
    CalendarEvent, DocumentTemplate
)


# ============================================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'role_display', 'avatar', 'profile_url',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


# ============================================================================
# РЕАГЕНТЫ
# ============================================================================

class ReagentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели реагента"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_critical = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Reagent
        fields = [
            'id', 'name', 'category', 'category_display', 'on_hand',
            'min_threshold', 'expiry_date', 'image', 'certificate',
            'external_link', 'is_critical', 'is_expiring_soon',
            'created_at', 'updated_at', 'url'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_critical(self, obj):
        return obj.is_critical()
    
    def get_is_expiring_soon(self, obj):
        return obj.is_expiring_soon()
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()


class ReagentMovementSerializer(serializers.ModelSerializer):
    """Сериализатор для движений реагентов"""
    reagent_name = serializers.CharField(source='reagent.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = ReagentMovement
        fields = [
            'id', 'reagent', 'reagent_name', 'quantity', 'movement_type',
            'movement_type_display', 'date', 'comment', 'user', 'user_name'
        ]
        read_only_fields = ['date']


# ============================================================================
# РЕЦЕПТУРЫ
# ============================================================================

class RecipeReagentSerializer(serializers.ModelSerializer):
    """Сериализатор для реагентов в рецептуре"""
    reagent_name = serializers.CharField(source='reagent.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    class Meta:
        model = RecipeReagent
        fields = ['id', 'reagent', 'reagent_name', 'quantity', 'unit', 'unit_display']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептур"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recipe_reagents = RecipeReagentSerializer(source='recipereagent_set', many=True, read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'author', 'author_name',
            'status', 'status_display', 'recipe_reagents',
            'created_at', 'updated_at', 'approved_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_at']


# ============================================================================
# КУЛЬТУРЫ
# ============================================================================

class CultureEventSerializer(serializers.ModelSerializer):
    """Сериализатор для событий культуры"""
    culture_name = serializers.CharField(source='culture.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = CultureEvent
        fields = [
            'id', 'culture', 'culture_name', 'event_type', 'event_type_display',
            'date', 'comment', 'user', 'user_name'
        ]
        read_only_fields = ['date']


class CultureSerializer(serializers.ModelSerializer):
    """Сериализатор для культур"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    responsible_name = serializers.CharField(source='responsible.username', read_only=True)
    recipe_name = serializers.CharField(source='recipe.name', read_only=True)
    recent_events = CultureEventSerializer(source='events', many=True, read_only=True)
    
    class Meta:
        model = Culture
        fields = [
            'id', 'name', 'status', 'status_display', 'seeding_date',
            'passage_number', 'recipe', 'recipe_name', 'responsible',
            'responsible_name', 'notes', 'recent_events'
        ]
        read_only_fields = ['seeding_date']


# ============================================================================
# ЗАДАЧИ
# ============================================================================

class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к задачам"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'user_name', 'text', 'date']
        read_only_fields = ['date']


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    comments = TaskCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assignee', 'assignee_name',
            'creator', 'creator_name', 'status', 'status_display',
            'priority', 'priority_display', 'deadline', 'is_overdue',
            'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


# ============================================================================
# ОБЪЯВЛЕНИЯ И КАЛЕНДАРЬ
# ============================================================================

class AnnouncementSerializer(serializers.ModelSerializer):
    """Сериализатор для объявлений"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'text', 'author', 'author_name',
            'published_at', 'is_pinned'
        ]
        read_only_fields = ['published_at']


class CalendarEventSerializer(serializers.ModelSerializer):
    """Сериализатор для событий календаря"""
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)
    participants_list = UserSerializer(source='participants', many=True, read_only=True)
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'subject', 'description', 'start_datetime', 'end_datetime',
            'organizer', 'organizer_name', 'participants', 'participants_list',
            'location'
        ]


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для документов"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'description', 'file', 'file_url',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


