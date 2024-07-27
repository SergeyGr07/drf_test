# Django REST Framework Project

## Описание

Этот проект представляет собой тествое веб-приложение на Django. Он использует Django Rest Framework (DRF) для создания RESTful API и SQLite в качестве базы данных. Проект упакован в Docker-контейнеры для простоты развертывания.

## Структура проекта

- `Dockerfile` - Конфигурация для создания Docker-образа.
- `docker-compose.yaml` - Конфигурация Docker Compose для запуска приложения.
- `db/` - Папка для хранения базы данных SQLite.
- `drf_test/` - Основной Django проект, содержащий настройки, URL и WSGI файл.
- `manage.py` - Утилита командной строки Django.
- `requirements.txt` - Список зависимостей Python.
- `test_app/` - Приложение Django, содержащее модели, сериализаторы, представления и тесты.

## Установка и запуск

### Системные требования

- Docker
- Docker Compose

### Запуск проекта

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/SergeyGr07/drf_test
   cd drf_test
   ```

2. **Соберите и запустите контейнеры:**

    ```bash
    docker compose build
    docker compose up -d
    ```

3. **Проверьте работу приложения:**

    Откройте браузер и перейдите по адресу: <http://localhost:8000>

4. **Вход в контейнер:**

    ```bash
    docker exec -it <CONTAINER ID> /bin/bash
    ```

5. **Примените миграции:**

    ```bash
    python manage.py migrate
    ```

6. **Создание суперпользователя:**

    ```bash
    python/python3 manage.py createsuperuser
    ```

7. **Запуск тестов:**

    ```bash
    python/python3 manage.py test
    ```
