import json
from projectsautomation.wsgi import *
from bot.models import Manager

if __name__ == '__main__':

    try:
        with open('managers.json', 'r', encoding='utf-8') as file:
            managers_json = json.load(file)
        for data in managers_json:
            Manager.objects.create(
                name=data['name'],
                tg_id=data['tg_id'],
                time=data['time']
            )
        print('Менеджеры успешно созданы из JSON файла.')
    except FileNotFoundError:
        print("Файл managers.json не найден.")
    except json.JSONDecodeError:
        print("Ошибка при декодировании JSON.")

