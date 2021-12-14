# chaplinskiy/hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

Учебный проект 6 спринта факультета бэкенд-разработки [Яндекс.Практикума](https://practicum.yandex.ru/backend-developer)

## Стек:
- Python
- Django
- Зоопарк из `requirements.txt`

Автотесты и всё такое (см. директорию `tests/`).

---
## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/chaplinskiy/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv env
```

```bash
source venv/bin/activate
```

```bash
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
cd yatube/ && python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```

Запуск `pytest`:

*из корневой папки, при запущенном виртуальном окружении*
```bash
pytest
```

### Шаблон наполнения env-файла
см.
```bash
.env.template
```


## Другие проекты автора:
https://github.com/chaplinskiy/