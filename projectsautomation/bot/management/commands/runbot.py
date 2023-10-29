import os
from django.core.management.base import BaseCommand
import time
import telebot
from telebot import types
from dotenv import load_dotenv
from .trello import create_board, get_board_id, add_member
from ...models import Student, Manager

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
        markup = types.InlineKeyboardMarkup(row_width=1)

        if manager:
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

