"""
Скрипт для создания тестовых данных
Запуск: python manage.py shell < create_test_data.py
"""

import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ddc_intranet.settings')
django.setup()

from django.utils import timezone
from intranet.models import (
    User, Reagent, ReagentMovement, Recipe, RecipeReagent,
    Culture, CultureEvent, Task, TaskComment, Announcement,
    CalendarEvent, DocumentTemplate
)

print("Creating test users...")

# Создаём пользователей
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ddc.com',
        'first_name': 'Администратор',
        'last_name': 'Системы',
        'role': 'sysadmin',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"+ Created superuser: admin (password: admin123)")
else:
    print(f"+ Superuser admin already exists")

lab_head, created = User.objects.get_or_create(
    username='labhead',
    defaults={
        'email': 'labhead@ddc.com',
        'first_name': 'Ivan',
        'last_name': 'Petrov',
        'role': 'lab_head',
        'is_staff': True
    }
)
if created:
    lab_head.set_password('labhead123')
    lab_head.save()
    print(f"+ Created lab head: labhead (password: labhead123)")

employee, created = User.objects.get_or_create(
    username='employee',
    defaults={
        'email': 'employee@ddc.com',
        'first_name': 'Maria',
        'last_name': 'Sidorova',
        'role': 'employee'
    }
)
if created:
    employee.set_password('employee123')
    employee.save()
    print(f"+ Created employee: employee (password: employee123)")

print("\nCreating reagents...")

# Создаём реагенты
reagents_data = [
    {
        'name': 'DMEM (Среда Игла модифицированная Дульбекко)',
        'category': 'media',
        'on_hand': 500,
        'min_threshold': 100,
        'expiry_date': timezone.now().date() + timedelta(days=180)
    },
    {
        'name': 'FBS (Фетальная бычья сыворотка)',
        'category': 'media',
        'on_hand': 50,
        'min_threshold': 100,  # Критично!
        'expiry_date': timezone.now().date() + timedelta(days=90)
    },
    {
        'name': 'Трипсин-EDTA',
        'category': 'enzyme',
        'on_hand': 150,
        'min_threshold': 50,
        'expiry_date': timezone.now().date() + timedelta(days=120)
    },
    {
        'name': 'PBS (Фосфатно-солевой буфер)',
        'category': 'buffer',
        'on_hand': 1000,
        'min_threshold': 200,
        'expiry_date': timezone.now().date() + timedelta(days=365)
    },
    {
        'name': 'Пенициллин-Стрептомицин',
        'category': 'chemical',
        'on_hand': 20,
        'min_threshold': 50,  # Критично!
        'expiry_date': timezone.now().date() + timedelta(days=30)  # Истекает!
    },
    {
        'name': 'Anti-CD3 антитело',
        'category': 'antibody',
        'on_hand': 5,
        'min_threshold': 10,  # Критично!
        'expiry_date': timezone.now().date() + timedelta(days=60)
    },
]

for data in reagents_data:
    reagent, created = Reagent.objects.get_or_create(
        name=data['name'],
        defaults=data
    )
    if created:
        print(f"  + {reagent.name}")

print("\nCreating reagent movements...")

# Создаём движения для первого реагента
reagent1 = Reagent.objects.first()
if reagent1:
    ReagentMovement.objects.get_or_create(
        reagent=reagent1,
        quantity=100,
        movement_type='in',
        user=admin_user,
        comment='Delivery from supplier'
    )
    print(f"  + Reagent movement: {reagent1.name}")

print("\nCreating recipes...")

# Создаём рецептуры
recipe1, created = Recipe.objects.get_or_create(
    name='Complete medium for HEK293 cells',
    defaults={
        'description': 'Standard medium for HEK293 cell culture. Contains DMEM, 10% FBS and antibiotics.',
        'author': lab_head,
        'status': 'approved',
        'approved_at': timezone.now()
    }
)
if created:
    print(f"  + {recipe1.name}")

print("\nCreating cultures...")

# Создаём культуры
culture1, created = Culture.objects.get_or_create(
    name='HEK293 P15',
    defaults={
        'status': 'active',
        'passage_number': 15,
        'seeding_date': timezone.now() - timedelta(days=3),
        'recipe': recipe1,
        'responsible': employee,
        'notes': 'Culture in good condition, next passage in 2 days'
    }
)
if created:
    print(f"  + {culture1.name}")

culture2, created = Culture.objects.get_or_create(
    name='CHO-K1 P22',
    defaults={
        'status': 'active',
        'passage_number': 22,
        'seeding_date': timezone.now() - timedelta(days=5),
        'responsible': employee,
        'notes': 'Production culture for protein synthesis'
    }
)
if created:
    print(f"  + {culture2.name}")

print("\nCreating tasks...")

# Создаём задачи
task1, created = Task.objects.get_or_create(
    title='Order reagents',
    defaults={
        'description': 'Urgently order FBS and Penicillin-Streptomycin, stocks are critically low.',
        'assignee': lab_head,
        'creator': employee,
        'status': 'new',
        'priority': 'urgent',
        'deadline': timezone.now() + timedelta(days=2)
    }
)
if created:
    print(f"  + {task1.title}")

task2, created = Task.objects.get_or_create(
    title='Passage HEK293 culture',
    defaults={
        'description': 'Passage HEK293 P15 culture at 1:4 ratio',
        'assignee': employee,
        'creator': lab_head,
        'status': 'in_progress',
        'priority': 'high',
        'deadline': timezone.now() + timedelta(days=1)
    }
)
if created:
    print(f"  + {task2.title}")

task3, created = Task.objects.get_or_create(
    title='Update protocol documentation',
    defaults={
        'description': 'Need to update internal documentation for all laboratory protocols',
        'assignee': lab_head,
        'creator': admin_user,
        'status': 'new',
        'priority': 'normal',
        'deadline': timezone.now() + timedelta(days=14)
    }
)
if created:
    print(f"  + {task3.title}")

print("\nCreating announcements...")

# Создаём объявления
ann1, created = Announcement.objects.get_or_create(
    title='Scheduled equipment maintenance',
    defaults={
        'text': 'Dear colleagues! Next Friday from 14:00 to 16:00, scheduled maintenance will be performed on the laminar flow hood. Please take this into account when planning your work.',
        'author': lab_head,
        'is_pinned': True
    }
)
if created:
    print(f"  + {ann1.title}")

ann2, created = Announcement.objects.get_or_create(
    title='New rules for biological waste disposal',
    defaults={
        'text': 'Starting from the 1st, new rules for biological waste disposal will be introduced. All employees must undergo training with the responsible person.',
        'author': admin_user,
        'is_pinned': True
    }
)
if created:
    print(f"  + {ann2.title}")

ann3, created = Announcement.objects.get_or_create(
    title='Congratulations on successful project completion!',
    defaults={
        'text': 'The Alpha project team has successfully completed all research stages. Congratulations!',
        'author': lab_head,
        'published_at': timezone.now() - timedelta(days=2)
    }
)
if created:
    print(f"  + {ann3.title}")

print("\nCreating calendar events...")

# Создаём события календаря
event1, created = CalendarEvent.objects.get_or_create(
    subject='Weekly meeting',
    defaults={
        'description': 'Discussion of current projects and plans for the week',
        'start_datetime': timezone.now() + timedelta(days=1, hours=10),
        'end_datetime': timezone.now() + timedelta(days=1, hours=11),
        'organizer': lab_head,
        'location': 'Conference room'
    }
)
if created:
    event1.participants.add(employee, admin_user)
    print(f"  + {event1.subject}")

print("\n" + "="*50)
print("Test data successfully created!")
print("="*50)
print("\nAvailable accounts:")
print("1. admin / admin123 (System Administrator)")
print("2. labhead / labhead123 (Lab Head)")
print("3. employee / employee123 (Employee)")
print("\nRun server: python manage.py runserver")
print("Open: http://127.0.0.1:8000/")

