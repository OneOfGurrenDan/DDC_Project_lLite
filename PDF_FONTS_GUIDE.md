# 📄 Руководство по работе с TTF шрифтами в PDF

## ✅ Что было сделано

В файл `intranet/admin.py` добавлена поддержка кириллических шрифтов для генерации PDF-отчётов.

## 🔧 Изменения в коде

### 1. Импорты
```python
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
```

### 2. Регистрация TTF шрифта

Функция `export_to_pdf` теперь автоматически:
- **Ищет системный шрифт Arial** в `C:\Windows\Fonts\arial.ttf` (Windows)
- **Регистрирует шрифт** под именем `ArialCyrillic`
- **Использует fallback** на стандартный шрифт, если Arial не найден

```python
# Регистрация TTF шрифта
arial_path = "C:\\Windows\\Fonts\\arial.ttf"
if os.path.exists(arial_path):
    pdfmetrics.registerFont(TTFont('ArialCyrillic', arial_path))
    font_regular = 'ArialCyrillic'
```

### 3. Улучшения отчёта

Теперь PDF-отчёт включает:
- ✅ **Русский заголовок**: "DDC Biotech - Отчёт по реагентам"
- ✅ **Дата и время** создания отчёта
- ✅ **Имя пользователя**, создавшего отчёт
- ✅ **Таблица с данными**: Название, Категория, Остаток, Мин. порог
- ✅ **Футер** с общим количеством реагентов
- ✅ **Автоматическая пагинация** при переполнении страницы

## 📖 Как использовать

### Через админ-панель Django

1. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

2. Откройте админ-панель: `http://127.0.0.1:8000/admin/`

3. Перейдите в раздел **Reagent** (Реагенты)

4. Выберите нужные реагенты (чекбоксами)

5. В выпадающем меню **Action** выберите **"Экспорт в PDF"**

6. Нажмите **"Go"**

7. Браузер автоматически скачает файл `reagents_report.pdf` с кириллицей

## 🌐 Кросс-платформенность

### Windows
```python
arial_path = "C:\\Windows\\Fonts\\arial.ttf"
```

### Linux/Mac (добавьте в код, если нужно)
```python
# Linux
if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
    pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

# Mac
if os.path.exists("/System/Library/Fonts/Helvetica.ttc"):
    # Используйте системные шрифты Mac
```

## 📦 Добавление собственных шрифтов

Если хотите использовать специальный шрифт:

### 1. Скачайте TTF шрифт
Например, **DejaVu Sans** с поддержкой кириллицы:
- https://dejavu-fonts.github.io/

### 2. Поместите в проект
```
static/fonts/DejaVuSans.ttf
static/fonts/DejaVuSans-Bold.ttf
```

### 3. Зарегистрируйте в коде
```python
import os
from django.conf import settings

font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
    p.setFont('DejaVu', 12)
```

## 🎨 Дополнительные возможности ReportLab

### Цветной текст
```python
from reportlab.lib import colors

p.setFillColor(colors.red)
p.drawString(50, 700, "Критический остаток!")
p.setFillColor(colors.black)  # Вернуть черный
```

### Изображения
```python
p.drawImage("logo.png", 50, height - 100, width=100, height=50)
```

### Таблицы с границами
```python
from reportlab.platypus import Table, TableStyle

data = [
    ['Название', 'Остаток'],
    ['Реагент 1', '50'],
    ['Реагент 2', '30']
]

table = Table(data)
table.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
]))
```

### QR-коды
```python
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

qr = QrCodeWidget('https://ddc-biotech.com')
bounds = qr.getBounds()
width = bounds[2] - bounds[0]
height = bounds[3] - bounds[1]
d = Drawing(100, 100, transform=[100./width, 0, 0, 100./height, 0, 0])
d.add(qr)
```

## 🔍 Отладка

Если кириллица не отображается:

1. **Проверьте путь к шрифту:**
   ```python
   print(os.path.exists("C:\\Windows\\Fonts\\arial.ttf"))
   ```

2. **Проверьте регистрацию шрифта:**
   ```python
   from reportlab.pdfbase import pdfmetrics
   print(pdfmetrics.getRegisteredFontNames())
   ```

3. **Используйте отладку:**
   ```python
   try:
       pdfmetrics.registerFont(TTFont('Test', font_path))
       print("Шрифт зарегистрирован успешно!")
   except Exception as e:
       print(f"Ошибка: {e}")
   ```

## 📚 Полезные ссылки

- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [ReportLab на PyPI](https://pypi.org/project/reportlab/)
- [Примеры кода ReportLab](https://github.com/MrBitBucket/reportlab-mirror)
- [DejaVu Fonts](https://dejavu-fonts.github.io/)

## 💡 Советы

1. **Кэшируйте регистрацию шрифтов** - не регистрируйте один и тот же шрифт много раз
2. **Используйте системные шрифты** - они быстрее загружаются
3. **Проверяйте размер PDF** - большие изображения увеличивают размер файла
4. **Тестируйте на разных платформах** - пути к шрифтам различаются

---

**Автор:** DDC Biotech Dev Team  
**Дата:** Ноябрь 2024


