# DDC Biotech Интранет

Монолитное Django-приложение для внутреннего использования в биотехнологической компании DDC Biotech.

## Описание проекта

Студенческий курсовой проект, демонстрирующий создание полнофункционального интранет-портала для управления:
- Реагентами и химическими веществами
- Клеточными культурами
- Рецептурами и протоколами
- Задачами и комментариями
- Объявлениями и документами
- Календарём событий

## Технологический стек

- **Django 4.2.16** - веб-фреймворк
- **Django REST Framework 3.16.1** - REST API
- **SQLite** - база данных (с возможностью переключения на PostgreSQL)
- **Bootstrap 5** - фронтенд-фреймворк
- **Pillow** - обработка изображений
- **ReportLab** - генерация PDF
- **django-debug-toolbar** - инструмент отладки

## Требования

- Python 3.8+
- pip

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ddc_project_lite
```

### 2. Создание виртуального окружения

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

Админ-панель: http://127.0.0.1:8000/admin/

REST API: http://127.0.0.1:8000/api/

API аутентификация: http://127.0.0.1:8000/api-auth/login/

## Структура проекта

```
ddc_project_lite/
├── ddc_intranet/          # Конфигурация проекта
│   ├── settings.py        # Настройки Django
│   ├── urls.py            # Главные URL-маршруты
│   └── wsgi.py            # WSGI конфигурация
├── intranet/              # Основное приложение
│   ├── models.py          # Все модели данных
│   ├── views.py           # Все представления (FBV)
│   ├── forms.py           # Все формы
│   ├── admin.py           # Настройка админ-панели
│   ├── urls.py            # URL-маршруты приложения
│   └── templatetags/      # Пользовательские теги шаблонов
├── templates/             # HTML-шаблоны
│   ├── base.html          # Базовый шаблон
│   ├── dashboard.html     # Главная страница
│   ├── auth/              # Шаблоны аутентификации
│   ├── forms/             # Шаблоны форм
│   └── widgets/           # Виджеты для inclusion tags
├── static/                # Статические файлы
│   ├── css/               # CSS стили
│   └── js/                # JavaScript
├── media/                 # Загруженные файлы
├── requirements.txt       # Зависимости Python
└── README.md              # Этот файл
```

## Основные возможности

### Дашборд (Задание 15)

Главная страница содержит:
- 3 виджета с данными из разных таблиц
- Статистические карточки
- Функционал поиска по всем объектам
- Пагинацию

### CRUD Реагентов (Задание 16)

Полный набор операций:
- Просмотр списка реагентов с фильтрацией
- Детальная страница реагента
- Создание нового реагента
- Редактирование реагента
- Удаление реагента
- Контроль доступа по ролям

### Модели данных

Все модели включают:
- `__str__()` методы
- `verbose_name` и `verbose_name_plural`
- `related_name` для FK и M2M
- Поля: ImageField, FileField, URLField
- Кастомные менеджеры
- F-выражения в save()

### Формы

Демонстрация:
- ModelForm с различными виджетами
- Кастомная валидация через `clean_<field>()`
- Переопределённый `save(commit=True)`
- `class Media` для подключения JS/CSS
- Обработка загрузки файлов

### Представления (Views)

Все FBV демонстрируют:
- filter(), exclude(), order_by()
- Lookup'ы (__icontains, __contains)
- values(), values_list(), count(), exists()
- aggregate(), F(), Q()
- select_related(), prefetch_related()
- Пагинацию с try/except
- Работу с сессиями

### Админ-панель

Полная кастомизация:
- list_display, list_filter, search_fields
- date_hierarchy
- Inline-модели
- raw_id_fields, filter_horizontal
- readonly_fields
- Кастомные display-методы с @admin.display
- Admin actions (включая генерацию PDF)

### Шаблонные теги

Реализованы:
- Простые теги (@simple_tag)
- Контекстные теги (takes_context=True)
- Inclusion tags для виджетов
- Кастомные фильтры

## Роли пользователей

- **employee** - Сотрудник (базовые права)
- **lab_head** - Заведующий лабораторией (создание/редактирование)
- **sysadmin** - Системный администратор (все права)

## Настройка

### Переключение на PostgreSQL

1. Раскомментируйте зависимость в `requirements.txt`:
```python
psycopg2-binary==2.9.9
```

2. Установите PostgreSQL и создайте базу данных

3. В `ddc_intranet/settings.py` закомментируйте SQLite и раскомментируйте PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ddc_intranet',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Переключение DEBUG

В `settings.py`:
```python
# Для разработки
DEBUG = True

# Для демонстрации "боевого" режима
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Кеширование

Кеширование включено для главной страницы (5 минут). Настройки в `settings.py`.

## REST API

Проект включает полноценный REST API с поддержкой всех основных операций.

### Основные возможности API:
- Полный CRUD для всех моделей (реагенты, культуры, задачи и т.д.)
- Аутентификация через Session и Basic Auth
- Пагинация (20 элементов на странице)
- Поиск и фильтрация
- Сортировка результатов
- Browsable API интерфейс для тестирования

### Документация API:
Подробная документация доступна в файле `API_DOCUMENTATION.md`

### Основные endpoints:
- `http://127.0.0.1:8000/api/` - корень API
- `http://127.0.0.1:8000/api/reagents/` - реагенты
- `http://127.0.0.1:8000/api/tasks/` - задачи
- `http://127.0.0.1:8000/api/cultures/` - культуры
- `http://127.0.0.1:8000/api/recipes/` - рецептуры
- `http://127.0.0.1:8000/api/announcements/` - объявления
- `http://127.0.0.1:8000/api/documents/` - документы

## Дополнительные функции

- REST API с Django REST Framework
- Django Debug Toolbar (только в DEBUG=True)
- Кеширование представлений
- Интернационализация (русский язык)
- Обработка медиа-файлов
- Кастомные страницы ошибок (404, 500)

## Автор

Студенческий проект для курсовой работы

## Лицензия

Для образовательных целей

