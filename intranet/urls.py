"""
URL маршруты приложения intranet
"""

from django.urls import path, re_path
from . import views

urlpatterns = [
    # ========================================
    # ГЛАВНАЯ СТРАНИЦА
    # ========================================
    path('', views.dashboard, name='dashboard'),
    
    # ========================================
    # АУТЕНТИФИКАЦИЯ
    # ========================================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # ========================================
    # CRUD ОБЪЕКТОВ (РЕАГЕНТЫ) - Задание 16
    # ========================================
    path('objects/', views.object_list, name='object_list'),
    path('objects/<int:pk>/', views.object_detail, name='reagent_detail'),
    path('objects/create/', views.object_create, name='object_create'),
    path('objects/<int:pk>/edit/', views.object_update, name='object_update'),
    path('objects/<int:pk>/delete/', views.object_delete, name='object_delete'),
    
    # ========================================
    # РЕАГЕНТЫ
    # ========================================
    path('reagents/', views.reagent_list_filtered, name='reagent_list'),
    
    # ========================================
    # ЗАДАЧИ
    # ========================================
    path('tasks/', views.task_list, name='task_list'),
    
    # ========================================
    # КУЛЬТУРЫ
    # ========================================
    path('cultures/', views.culture_list, name='culture_list'),
    
    # ========================================
    # РЕЦЕПТУРЫ
    # ========================================
    path('recipes/', views.recipe_list, name='recipe_list'),
    
    # ========================================
    # ОБЪЯВЛЕНИЯ
    # ========================================
    path('announcements/', views.announcement_list, name='announcement_list'),
    
    # ========================================
    # ДОКУМЕНТЫ
    # ========================================
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    
    # ========================================
    # ПРИМЕРЫ С re_path() И РЕГУЛЯРНЫМИ ВЫРАЖЕНИЯМИ
    # ========================================
    # Пример: поиск реагента по slug (буквы, цифры, дефисы)
    re_path(r'^reagent-search/(?P<slug>[\w-]+)/$', views.object_list, name='reagent_search_slug'),
    
    # Пример: год в объявлениях (4 цифры)
    re_path(r'^announcements/(?P<year>\d{4})/$', views.announcement_list, name='announcements_by_year'),
    
    # Пример: ID с ведущими нулями
    re_path(r'^object/(?P<pk>\d+)/$', views.object_detail, name='object_detail_regex'),
]


