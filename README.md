
## Переменные окружения
Создайте файл .env.prod и заполните его. Используйте .env.prod.example в качестве примера.

## Docker
Запустите Docker контейнеры:
```console
make up
```

Выполнить миграции:
```console
make migrate
```

Создать суперпользователя:
```console
make createsuperuser
```

## Сервис авторизации
API доступно по адресу:
- $HOST/auth/api/


API доступно по адресу:
- $HOST/movies/api/
