"""
URL Configuration for ddc_intranet project
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('intranet.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('intranet.urls')),
]

# Обработка статики и медиа в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Кастомные обработчики ошибок
handler404 = 'intranet.views.custom_404'
handler500 = 'intranet.views.custom_500'
