## Foodgram

Cервис Foodgram предназначен для публикаций рецептов. На данном сервисе пользователи могут подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список избранных, а также скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Структура проекта
 * /frontend - файлы для сборки фронтенда приложения.
 * /backend - бэкенд foodgram на Django.
 * /nginx  — файлы для сборки контейнера gateway, пользовательская страница ошибки 404.
 * /data - список ингредиентов с единицами измерения (json, cvs).
 * /docs - файлы спецификации API.
 * /postman-collection - тесты API
 * файлы: docker-compose.production.yml и docker-compose.yml для оркестрации контейнеров на сервере и локальном компьютере


## Список возможностей Foodgram

#### Возможности авторизированных пользователей:
- Входить и выходить с сайта (пароль, email)
- Менять свой пароль.
- Создавать, редактировать и удалять свои рецепты
- Подписываться на публикации авторов рецептов и отменять подписку
- Просматривать свою страницу подписок.
- Работать с личным списком избранного:
  - добавлять рецепты и удалять их 
  - просматривать свою страницу избранных рецептов.
- Работать с личным списком покупок: 
  - добавлять и удалять любые рецепты, 
  - выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку
- Просматривать свою страницу подписок.
- Всё что могут не авторизированные пользователи

#### Возможности не авторизированных пользователей:
- Создать аккаунт.
- Просматривать рецепты на главной странице.
- Просматривать страницы рецептов.
- Просматривать рецепты на главной странице.
- Просматривать страницы рецептов.
- Просматривать профили пользователей.
- Фильтровать рецепты по тегам.

#### Возможности администраторов (в админ-панеле):
- Всё что могут авторизированные пользователи.
- изменять пароль любого пользователя
- создавать, удалять и деактивировать аккаунты пользователей,
- удалять и редактировать любые рецепты 
- добавлять, удалять и редактировать теги
- добавлять, удалять и редактировать ингредиенты


### Сайт и документация API доступена по ссылкам:

```
https://1food.sytes.net/
https://1food.sytes.net/api/docs/
```
данные для входа в админ-зону
электронная почта: 
food@foo.do
пароль
foodgram_password

## Инструкция по установке
### Локальная установка
Клонируйте репозиторий:
```
git@github.com:rete11/foodgram-project-react.git
```

В корневом каталоге создайте файл .env, с переменными окружения.

Создайте виртуальное окружение:
```
python -m venv venv
```
Активируйте виртуальное окружение

* для Windows:
```source venv/Scripts/activate```

* для Linux/Mac:
```source venv/bin/activate```

Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Чтобы работать с базой данных локально в файле foodgram/setting.py замените PostgreSQL на  SQLite:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

Примените миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Заитем соберите статику:
```
python manage.py collectstatic
```
Создайте суперпользователя:
```
python manage.py createsuperuser
```
Загрузите данные в модель :
```
python manage.py load_data
```
Перейдите в папку с файлом manage.py выполните команду для запуска локально:
```
python manage.py runserver
```


### Запуск проекта в контейнерах:

Установите docker и docker-compose.
[Информация по установке (Win/Mac/Linux)](https://docs.docker.com/compose/install/)

- Linux:
```
sudo apt install curl                                   
curl -fsSL https://get.docker.com -o get-docker.sh      
sh get-docker.sh                                        
sudo apt-get install docker-compose-plugin              
```


Cоздайте и заполните .env файл в корневом каталоге 
```
DEBUG=False
ALLOWED_HOSTS=ip-сервера,127.0.0.1,localhost,example.com
CSRF_TRUSTED_ORIGINS = https://example.com/,https://ip-сервера/
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=postgres
POSTGRES_PASSWORD=password
POSTGRES_USER=user
SECRET_KEY=django-insecure-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```
Из корневой папки разверните контейнеры при помощи docker-compose:
```
docker-compose up -d --build
```
Примените миграции:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
Соберите статику:
```
docker-compose exec backend python manage.py collectstatic
```
Наполните базу данных. 
```
docker-compose exec backend python manage.py load_data
```
Проект будетдоступен по адресу:
```
http://127.0.0.1:8000/
```

Cписок эндпоинтов API:
```
- /api/users/ - список пользователей (page, limit), 
регистрация (email, username, first_name, last_name, password), 
профиль (id), текущий, изменение пароля (new_password, current_password), получение и удаление токена (password, email).
- /api/tags/ - список тегов, получение тега (id).
- /api/recipes/ - список рецептов (page, limit, is_favorited, is_in_shopping_cart, author, tags), создание (ingredients, tags, image, name, text, cooking_time), получение (id), обновление (id, ingredients, tags, image, name, text, cooking_time), удаление (id).
- /api/recipes/download_shopping_cart/ - скачать список покупок.
- /api/recipes/{id}/shopping_cart/ - добавить или удалить рецепт из списка покупок.
- /api/recipes/{id}/favorite/ - добавить или удалить рецепт из избранного.
- /api/users/subscriptions/ - мои подписки (page, limit, recipes_limit).
- /api/users/{id}/subscribe/ - подписаться или отписаться от пользователя (recipes_limit).
- /api/ingredients/ - список ингредиентов (name), получение ингредиента (id).
```
