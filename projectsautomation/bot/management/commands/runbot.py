import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
import time
import telebot
from telebot import types
from dotenv import load_dotenv
from .trello import create_board, get_board_id, add_member
from ...models import Student, Manager

from ...models import Student, Manager, Administrator, Project
from .trello import create_board, get_boards_id, add_member, create_organization, get_organization


load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.chat.id
        user_name = message.from_user.first_name
        student = Student.objects.filter(tg_id=user_id).first()
        manager = Manager.objects.filter(tg_id=user_id).first()
        administrator = Administrator.objects.filter(tg_id=user_id).first()
        markup = types.InlineKeyboardMarkup(row_width=1)

        if administrator:
            item1 = types.InlineKeyboardButton('Cписок учеников', callback_data='students_info')
            item2 = types.InlineKeyboardButton('Cписок менеджеров', callback_data='pms_info')
            item3 = types.InlineKeyboardButton('Сгенерировать команды', callback_data='create_comands')
            item4 = types.InlineKeyboardButton('Оповестить о проекте', callback_data='send_alert')
            markup.add(item1, item2, item3, item4)
            welcome_message = f'Привет, {user_name}!'
            bot.send_message(user_id, text=welcome_message, reply_markup=markup)
        elif manager:
            item1 = types.InlineKeyboardButton('Изменить время', callback_data='change_time')
            item2 = types.InlineKeyboardButton('Инфа о командах', callback_data='team_info')
            item3 = types.InlineKeyboardButton('Создать доску', callback_data='create_project')
            markup.add(item1, item2, item3)
            welcome_message = f'Привет, {user_name}!'
            bot.send_message(user_id, text=welcome_message, reply_markup=markup)

        elif student:
            if student.projects.exists():
                button_text = 'Отменить проект'
                callback_data = 'cancel_project'
            else:
                button_text = 'Записаться на проект'
                callback_data = 'sing_in'
            sign_in_button = types.InlineKeyboardButton(button_text, callback_data=callback_data)
            item2 = types.InlineKeyboardButton('Связаться с ПМ', callback_data='message_to_pm')
            item3 = types.InlineKeyboardButton('Информация о проекте', callback_data='project_info')
            markup.add(sign_in_button, item2, item3)
            welcome_message = f'Привет, {user_name}!'
            bot.send_message(user_id, text=welcome_message, reply_markup=markup)

        else:
            welcome_message = f'Привет, {user_name}! Вас еще не добавили в базу данных. Подождите и мы все исправим'
            bot.send_message(user_id, text=welcome_message, reply_markup=markup)



    @bot.callback_query_handler(func=lambda call: call.data == 'send_alert')
    def send_project_alert(call):
        projects = Project.objects.all()
        print(projects)
        for project in projects:
            students = project.students.all()
            print(students)
            alert_message = f'Уважаемые участники проекта "{project.name}"!\n\n'
            project_info = f'Проект начнется {project.date} в {project.time}. Участвующие ученики: {", ".join([participant.name for participant in students])}\n\n'
            alert_message += project_info

            for student in students:
                bot.send_message(chat_id=student.tg_id,
                                 text=alert_message)

        bot.send_message(call.message.chat.id, 'Оповещение о всех проектах отправлено всем участникам.')

    @bot.message_handler(func=lambda message: True)
    def process_project_name(message):
        project_name = message.text
        project_data[message.chat.id] = {'name': project_name}
        bot.send_message(message.chat.id,
                         f'Название проекта: {project_name}\nВведите дату начала проекта')
        bot.register_next_step_handler(message, process_start_time)



    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.message:
            if call.data == 'change_time':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('10:00 - 14:00', callback_data='pm_time#1')
                item2 = types.InlineKeyboardButton('14:00 - 18:00', callback_data='pm_time#2')
                item3 = types.InlineKeyboardButton('18:00 - 22:00', callback_data='pm_time#3')
                markup.add(item1, item2, item3)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nКогда тебе удобно взять учеников?',
                                      parse_mode='Markdown', reply_markup=markup)

            elif 'pm_time' in call.data:
                markup = types.InlineKeyboardMarkup(row_width=1)
                flag = call.data.split('#')[1]
                if flag == '1':
                    time = '10:00 - 14:00'
                elif flag == '2':
                    time = '14:00 - 18:00'
                else:
                    time = '18:00 - 22:00'
                item1 = types.InlineKeyboardButton('Назад', callback_data='change_time')
                markup.add(item1)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nТы выбрал период: {time}',
                                      parse_mode='Markdown', reply_markup=markup)


            elif call.data == 'team_info':
                manager_tg_id = call.message.chat.id
                manager = Manager.objects.filter(tg_id=manager_tg_id).first()

                if manager is not None and manager.projects.exists():
                    projects_info = ""
                    for project in manager.projects.all():
                        project_info = f'\nПроект: "{project.name}"\n'
                        project_info += 'Команда:\n'
                        for index, student in enumerate(project.students.all(), start=1):
                            project_info += f'"{index}. {student.name}"\n'
                        project_info += f'Время созвона: {project.time}\n'
                        project_info += f'Дата созвона: {project.date.strftime("%Y-%m-%d")}\n'
                        projects_info += project_info
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id, text=projects_info)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id, text='\nПроекты еще не созданы админом.')


            elif call.data == 'create_project':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Назад', callback_data='pm')
                markup.add(item1)
                project_name = call.message.text
                create_board(project_name)
                board_id = get_board_id(project_name)
                """Присылает на почту приглашение на доску, но только один раз.
                Чтобы прислал еще раз необходимо удалить доску"""
                add_member(board_id, call.message.chat.username, 'artemvlmorozov@gmail.com')
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\n Доска создана',
                                      reply_markup=markup)

            elif call.data == 'sing_in':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('14:00-18:00', callback_data='entry#1')
                item2 = types.InlineKeyboardButton('18:00-22:00', callback_data='entry#2')
                item3 = types.InlineKeyboardButton('Любое время', callback_data='entry#3')
                markup.add(item1, item2, item3)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='\nКогда тебе удобно участвовать в проекте?',
                                      parse_mode='Markdown', reply_markup=markup)


            elif call.data.startswith('entry'):
                flag = call.data.split('#')[1]
                student_id=call.message.chat.id
                student = Student.objects.get(tg_id=student_id)
                if flag == '1':
                    student.time = 1
                elif flag == '2':
                    student.time = 2
                elif flag == '3':
                    student.time = 3
                student.save()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nТы записан на {student.get_time_display()}.\nПозже с тобой свяжется ПМ',
                                      parse_mode='Markdown')


            elif call.data == 'message_to_pm':
                student_tg_id = call.message.chat.id
                student = Student.objects.filter(tg_id=student_tg_id).first()
                if student is not None and student.projects.exists():
                    current_project = student.projects.first()
                    pm_name = current_project.manager.name
                    bot.send_message(chat_id=student_tg_id,
                                     text=f'Пожалуйста, напишите ваше сообщение для {pm_name}. Я его передам.',
                                     reply_markup=types.ForceReply(selective=True))
                else:
                    bot.send_message(chat_id=student_tg_id,
                                     text='\nТы еще не в проекте.')



            elif call.data == 'project_info':
                student_tg_id = call.message.chat.id
                student = Student.objects.filter(tg_id=student_tg_id).first()
                if student is not None and student.projects.exists():
                    project = student.projects.first()
                    project_info = f'\nТвой проект: "{project.name}"\n'
                    project_info += 'Команда:\n'
                    for index, student in enumerate(project.students.all(), start=1):
                        project_info += f'"{index}. {student.name}"\n'
                    project_info += f'Ваш ПМ: "{project.manager.name}"\n'
                    project_info += f'Время созвона: {project.time}\n'
                    project_info += f'Дата созвона: {project.date.strftime("%Y-%m-%d")}\n'
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id, text=project_info)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id, text='\nТы еще не присоединен к проекту.')


            elif call.data == 'cancel_project':
                student_tg_id = call.message.chat.id
                student = Student.objects.filter(tg_id=student_tg_id).first()
                if student is not None and student.projects.exists():
                    project = student.projects.first()
                    student.projects.remove(project)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id,
                                          text='\nВы успешно отменили свое участие в проекте.')


            elif call.data == 'students_info':
                students = Student.objects.all()
                students_info = ""
                for student in students:
                    students_info += f'TG_ID: {student.tg_id}, Имя: {student.name}, Навыки: {student.get_skills_display()},Доступное время: {student.get_time_display()}\n\n'
                if students_info:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id,
                                          text=students_info)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id,
                                          text='\nСтудентов нет в базе данных.')

            elif call.data == 'pms_info':
                managers = Manager.objects.all()
                managers_info = ""
                for manager in managers:
                    managers_info += f'TG_ID: {manager.tg_id}, Имя: {manager.name}, Доступное время: {manager.get_time_display()}\n\n'
                if managers_info:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id,
                                          text=managers_info)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id,
                                          text='\nМенеджеров нет в базе данных.')

            elif call.data == 'create_comands':
                today = datetime.now().date()
                tomorrow = today + timedelta(days=1)
                group_size = 3

                morning_beginners = list(Student.objects.filter(time=1, skills=1))
                evening_beginners = list(Student.objects.filter(time=2, skills=1))
                any_time_beginners = list(Student.objects.filter(time=3, skills=1))

                groups_beginners = []
                for students in [evening_beginners, morning_beginners]:
                    students.sort(key=lambda x: x.time, reverse=True)
                    for i in range(0, len(students), group_size):
                        group = list(students[i:i + group_size])
                        groups_beginners.append(group)

                for student in any_time_beginners:
                    added_to_group = False
                    for group in groups_beginners:
                        if len(group) < group_size:
                            group.append(student)
                            added_to_group = True
                            break
                    if not added_to_group:
                        groups_beginners.append([student])

                morning_advanced = list(Student.objects.filter(time=1, skills=2))
                evening_advanced = list(Student.objects.filter(time=2, skills=2))
                any_time_advanced = list(Student.objects.filter(time=3, skills=3))
                groups_advanced = []

                for students in [evening_advanced, morning_advanced]:
                    students.sort(key=lambda x: x.time, reverse=True)
                    for i in range(0, len(students), group_size):
                        group = list(students[i:i + group_size])
                        groups_advanced.append(group)

                for student in any_time_advanced:
                    added_to_group = False
                    for group in groups_advanced:
                        if len(group) < group_size:
                            group.append(student)
                            added_to_group = True
                            break
                    if not added_to_group:
                        groups_advanced.append([student])

                morning_experts = list(Student.objects.filter(time=1, skills=3))
                evening_experts = list(Student.objects.filter(time=2, skills=3))
                any_time_experts = list(Student.objects.filter(time=3, skills=3))
                groups_experts = []

                for students in [evening_experts, morning_experts]:
                    students.sort(key=lambda x: x.time, reverse=True)
                    for i in range(0, len(students), group_size):
                        group = list(students[i:i + group_size])
                        groups_experts.append(group)

                for student in any_time_experts:
                    added_to_group = False
                    for group in groups_experts:
                        if len(group) < group_size:
                            group.append(student)
                            added_to_group = True
                            break
                    if not added_to_group:
                        groups_experts.append([student])

                managers = list(Manager.objects.all())
                projects = []

                for i, (beginner_group, advanced_group, expert_group) in enumerate(
                        zip(groups_beginners, groups_advanced, groups_experts), start=1):
                    beginner_manager = managers[i % len(managers)]
                    advanced_manager = managers[(i + 1) % len(managers)]
                    expert_manager = managers[(i + 2) % len(managers)]

                    beginner_project = Project(
                        name=f"Начинающая группа {i}",
                        manager=beginner_manager,
                        time=beginner_group[0].time,
                        date=tomorrow
                    )
                    beginner_project.save()
                    beginner_project.students.set(
                        beginner_group)

                    advanced_project = Project(
                        name=f"Продвинутая группа {i}",
                        manager=advanced_manager,
                        time=advanced_group[0].time,
                        date=tomorrow
                    )
                    advanced_project.save()
                    advanced_project.students.set(advanced_group)

                    expert_project = Project(
                        name=f"Экспертная группа {i}",
                        manager=expert_manager,
                        time=expert_group[0].time,
                        date=tomorrow
                    )
                    expert_project.save()
                    expert_project.students.set(expert_group)

                    projects.extend([beginner_project, advanced_project, expert_project])

                project_info = "Созданные проекты на завтрашний день:\n"
                for i, project in enumerate(projects, start=1):
                    project_info += f"Проект {i}:\n"
                    project_info += f"Название: {project.name}\n"
                    project_info += f"Менеджер: {project.manager.name}\n"

                    beginner_students = project.students.filter(skills=1)
                    advanced_students = project.students.filter(skills=2)
                    expert_students = project.students.filter(skills=3)

                    if beginner_students.exists():
                        project_info += f"Группа начинающих: {', '.join([student.name for student in beginner_students])}\n"
                    if advanced_students.exists():
                        project_info += f"Группа продвинутых: {', '.join([student.name for student in advanced_students])}\n"
                    if expert_students.exists():
                        project_info += f"Группа экспертов: {', '.join([student.name for student in expert_students])}\n"

                    project_info += f"Время: {project.time}\n"
                    project_info += f"Дата: {project.date}\n\n"

                bot.send_message(chat_id=call.message.chat.id, text=project_info)



    @bot.message_handler(func=lambda message: True)
    def handle_user_message(message):
        student_tg_id = message.chat.id
        student = Student.objects.filter(tg_id=student_tg_id).first()

        if student is not None and student.projects.exists():
            current_project = student.projects.first()
            pm_chat_id = current_project.manager.tg_id

            pm_message = f'Сообщение от ученика {student.name} (ID: {student_tg_id}):\n\n{message.text}'
            bot.send_message(chat_id=pm_chat_id,
                             text=pm_message)
            bot.send_message(chat_id=student_tg_id,
                             text='Ваше сообщение было успешно отправлено ПМу.')

    def handle(self, *args, **options):
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as error:
                print(error)
                time.sleep(5)
            command = input("Введите команду: ")
            if command.lower() == "stop":
                running = False

