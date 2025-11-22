"""
URL маршруты для REST API интранета DDC Biotech
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    UserViewSet, ReagentViewSet, ReagentMovementViewSet,
    RecipeViewSet, CultureViewSet, CultureEventViewSet,
    TaskViewSet, TaskCommentViewSet, AnnouncementViewSet,
    CalendarEventViewSet, DocumentTemplateViewSet
)

# Создаем роутер для автоматической генерации URL
router = DefaultRouter()

# Регистрируем ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'reagents', ReagentViewSet, basename='reagent')
router.register(r'reagent-movements', ReagentMovementViewSet, basename='reagent-movement')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'cultures', CultureViewSet, basename='culture')
router.register(r'culture-events', CultureEventViewSet, basename='culture-event')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'task-comments', TaskCommentViewSet, basename='task-comment')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'calendar-events', CalendarEventViewSet, basename='calendar-event')
router.register(r'documents', DocumentTemplateViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]


