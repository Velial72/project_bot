# Сервис ProjectsAutomation

Бот формирует команды для учебных проектов.
## Установка 

Установите [python3](https://realpython.com/installing-python/).

## Репозиторий
Клонируйте репозиторий в удобную папку.

## Виртуальное окружение
В терминале перейдите в папку с репозиторием.

### Создание виртуального окружения
```bush 
python3 -m venv venv
```

### Активация виртуального окружения

```
source venv/bin/activate
```

### Установка библиотек

```bush 
pip3 install -r requirements.txt
```
Создайте файл **.env** вида:
```properties
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_TOKEN
TRELLO_KEY=YOUR_PAYMENTS_TOKEN
TRELLO_TOKEN=YOUR_BOT_LINK
```
Получить [TELEGRAM_BOT_TOKEN](https://telegram.me/BotFather).

Получить [TRELLO_KEY и TRELLO_TOKEN](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/).
## Запуск
Создайте базу данных:

```bush
python3 manage.py makemigrations
python3 manage.py migrate
```
Создайте суперпользователя
```bush
python3 manage.py createsuperuser
```
Из директории с проектом запустите сайт командой.

```bush
python manage.py runbot
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
