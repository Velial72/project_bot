import json
from projectsautomation.wsgi import *
from bot.models import Student

if __name__ == '__main__':

    try:
        with open('students.json', 'r', encoding='utf-8') as file:
            students_json = json.load(file)
        for data in students_json:
            Student.objects.create(
                name=data['name'],
                tg_id=data['tg_id'],
                skills=data['skills'],
                time=data['time'],
                place_residence=data['place_residence'],
                is_active=data['is_active'],
                email=data['email']

            )
        print('Cтуденты успешно созданы из JSON файла.')
    except FileNotFoundError:
        print("Файл students.json не найден.")
    except json.JSONDecodeError:
        print("Ошибка при декодировании JSON.")
