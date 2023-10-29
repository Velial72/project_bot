import os
from django.core.management.base import BaseCommand
import time
import telebot
from telebot import types
from dotenv import load_dotenv
from ...models import Student, Manager, Project
from .trello import create_board, get_boards_id, add_member, create_organization, get_organization



load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)

project_data = {}
# Словарь для отслеживания текущего состояния
user_state = {}


def process_start_time(message):
    start_time = message.text
    project_data[message.chat.id]['start_time'] = start_time
    bot.send_message(message.chat.id,
                     f'Дата начала проекта: {start_time}\nВведите дату завершения проекта')
    bot.register_next_step_handler(message, process_end_time)


def process_end_time(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Создать проект', callback_data='create_project')
    markup.add(item1)
    end_time = message.text
    project_data[message.chat.id]['end_time'] = end_time
    bot.send_message(message.chat.id, 'Датa завершения проекта: ' + end_time)
    bot.send_message(message.chat.id, 'Данные о проекте сохранены.', reply_markup=markup)


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.chat.id
        user_name = message.from_user.first_name
        student = Student.objects.filter(tg_id=user_id).first()
        manager = Manager.objects.filter(tg_id=user_id).first()
        markup = types.InlineKeyboardMarkup(row_width=1)

        if True:
            item1 = types.InlineKeyboardButton('Изменить время', callback_data='change_time')
            item2 = types.InlineKeyboardButton('Инфа о командах', callback_data='team_info')
            item3 = types.InlineKeyboardButton('Создать проект на Trello', callback_data='trello')
            item4 = types.InlineKeyboardButton('Создать доску', callback_data='choose_project')
            markup.add(item1, item2, item3, item4)
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

    @bot.message_handler(func=lambda message: True)
    def process_project_name(message):
        project_name = message.text
        project_data[message.chat.id] = {'name': project_name}
        bot.send_message(message.chat.id,
                         f'Название проекта: {project_name}\nВведите дату начала проекта')
        bot.register_next_step_handler(message, process_start_time)


    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        chat_id = call.message.chat.id
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


            elif call.data == 'trello':

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\n Введите название проекта',
                                      )
            elif call.data == 'choose_project':
                user_state[chat_id] = 'choose_organization'
                organizations = get_organization()
                markup = types.InlineKeyboardMarkup(row_width=1)
                if organizations:
                    for organization_num, organization in enumerate(organizations):
                        item_organization_num = types.InlineKeyboardButton(f'{organization["displayName"]}', callback_data=f'create_board_{organization["id"]}')
                        markup.add(item_organization_num)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id, text='\n В каком проекте создать доску?',
                                          reply_markup=markup)
                else:
                    item1 = types.InlineKeyboardButton('Создать проект на Trello', callback_data='trello')
                    markup.add(item1)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.message.id, text='\n Проекты не найдены. Создайте.',
                                          reply_markup=markup)

            elif call.data.startswith('create_board_') and user_state.get(chat_id) == 'choose_organization':
                selected_organization_id = call.data[len('create_board_'):]
                students_values = Student.objects.all().values_list('name', flat=True)
                students_list = list(students_values)
                students = ', '.join(students_list)
                # for i in range(3):
                #     create_board(f'"21:30":{students}', selected_organization_id)
                boards = get_boards_id(selected_organization_id)
                for board in boards:
                    # """Присылает на почту приглашение на доску, но только один раз.
                    # Чтобы прислал еще раз необходимо удалить доску"""
                    if not board['closed']:
                        for student in students_list:
                            add_member(board['id'], student, 'artemvlmorozov@gmail.com')
                bot.send_message(chat_id, f'Доска создана, ученики добавлены и уведомлены')

            elif call.data == 'create_project':
                create_organization(
                    project_data[call.message.chat.id]['name'],
                    project_data[call.message.chat.id]['start_time'],
                    project_data[call.message.chat.id]['end_time']
                    )
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\n Проект создан',
                                      )


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

