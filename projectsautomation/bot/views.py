import os
import json
import telebot
import random
from itertools import zip_longest
from telegram.error import TelegramError
from datetime import datetime, timedelta
from dotenv import load_dotenv
from django.http import HttpResponse
from .models import Student, Manager, Project
import logging



logging.basicConfig(filename='error.log', level=logging.ERROR)
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)

def import_students(request):
    try:
        with open('students.json', 'r', encoding='utf-8') as file:
            students_json = json.load(file)
        for data in students_json:
            tg_id = data['tg_id']
            existing_student = Student.objects.filter(tg_id=tg_id).first()
            if existing_student:
                existing_student.name = data['name']
                existing_student.time = data['time']
                existing_student.save()
            else:
                Student.objects.create(
                    name=data['name'],
                    tg_id=tg_id,
                    skills=data['skills'],
                    time=data['time'],
                    place_residence=data['place_residence'],
                    is_active=data['is_active'],
                    email=data['email']
                )
        return HttpResponse('Cтуденты успешно созданы/обновлены из JSON файла.')
    except FileNotFoundError:
        return HttpResponse('Файл students.json не найден.')
    except json.JSONDecodeError:
        return HttpResponse('Ошибка при декодировании JSON.')


def import_managers(request):
    try:
        with open('managers.json', 'r', encoding='utf-8') as file:
            managers_json = json.load(file)
        for data in managers_json:
            tg_id = data['tg_id']
            existing_manager = Manager.objects.filter(tg_id=tg_id).first()
            if existing_manager:
                existing_manager.name = data['name']
                existing_manager.time = data['time']
                existing_manager.save()
            else:
                Manager.objects.create(
                    name=data['name'],
                    tg_id=tg_id,
                    time=data['time']
                )
        return HttpResponse('Менеджеры успешно созданы/обновлены из JSON файла.')
    except FileNotFoundError:
        return HttpResponse('Файл managers.json не найден.')
    except json.JSONDecodeError:
        return HttpResponse('Ошибка при декодировании JSON.')


def generate_groups(request):
    tomorrow = datetime.now() + timedelta(days=1)

    students = list(Student.objects.all())
    managers = list(Manager.objects.all())

    juniors = [student for student in students if student.skills == 3]
    beginners_plus = [student for student in students if student.skills == 2]
    beginners = [student for student in students if student.skills == 1]

    groups = []
    for skill_group in [juniors, beginners_plus, beginners]:
        specific_time_students = [student for student in skill_group if student.time in [1, 2]]  # 14:00-18:00 и 18:00-22:00
        anytime_students = [student for student in skill_group if student.time == 3]  # Любое время

        while len(specific_time_students) >= 3:
            group = [specific_time_students.pop(0) for _ in range(3)]
            groups.append(group)

        while len(specific_time_students) > 0 and len(anytime_students) > 0:
            group = [specific_time_students.pop(0), anytime_students.pop(0)]
            if len(specific_time_students) > 0:
                group.append(specific_time_students.pop(0))
            groups.append(group)

        while len(anytime_students) >= 3:
            group = [anytime_students.pop(0) for _ in range(3)]
            groups.append(group)

        while len(specific_time_students) >= 2:
            group = [specific_time_students.pop(0) for _ in range(2)]
            groups.append(group)

        while len(anytime_students) >= 2:
            group = [anytime_students.pop(0) for _ in range(2)]
            groups.append(group)

        if len(specific_time_students) == 1:
            groups.append([specific_time_students.pop()])

        if len(anytime_students) == 1:
            groups.append([anytime_students.pop()])

    projects = []
    for group in groups:
        manager = random.choice(managers)

        project = Project.objects.create(name='Новый проект', manager=manager, time='12:00', date=tomorrow.date())
        for student in group:
            project.students.add(student)
        projects.append(project)

    return HttpResponse('Группы успешно сгенерированы и сохранены в базе данных.')


def send_alert(request):
    projects = Project.objects.all()
    error_messages = []

    for project in projects:
        students = project.students.all()
        manager = project.manager
        alert_message = f'Уважаемые участники проекта "{project.name}"!\n\n'

        project_info = f'Проект начнется {project.date} в {project.time}. Участвующие ученики: {", ".join([participant.name for participant in students])}\n\n'
        alert_message += project_info

        manager_info = f'Менеджер проекта: {manager.name}\n\n'
        alert_message += manager_info

        for student in students:
            try:
                bot.send_message(chat_id=student.tg_id, text=alert_message)
            except Exception as e:
                error_messages.append(f"Ошибка при отправке сообщения студенту {student.name}: {e}")

        try:
            bot.send_message(chat_id=manager.tg_id, text=alert_message)
        except Exception as e:
            error_messages.append(f"Ошибка при отправке сообщения менеджеру {manager.name}: {e}")

    if error_messages:
        for error_message in error_messages:
            logging.error(error_message)

    return HttpResponse('Оповещение о всех проектах отправлено всем участникам и менеджерам.')
