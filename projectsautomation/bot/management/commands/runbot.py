import os
from django.core.management.base import BaseCommand
import time
import telebot
from telebot import types
from dotenv import load_dotenv
from .trello import create_board, get_board_id, add_member
from ...models import Student

load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    @bot.message_handler(commands=['start'])
    def start(message):
        student_id = message.chat.id
        student_name = message.from_user.first_name
        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('Записаться на проект', callback_data='sing_in')
        item2 = types.InlineKeyboardButton('Связаться с ПМ', callback_data='message_to_pm')
        item3 = types.InlineKeyboardButton('Информация о проекте', callback_data='project_info')
        markup.add(item1, item2, item3)

        welcome_message = f'Привет, {student_name}!\nКакой у тебя вопрос?'
        bot.send_message(student_id, text=welcome_message, reply_markup=markup)


    @bot.message_handler(commands=['pm'])
    def set_name_project(message):
        if message.from_user.id == 66907613:
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('Изменить время', callback_data='change_time')
            item2 = types.InlineKeyboardButton('Инфа о командах', callback_data='team_info')
            item3 = types.InlineKeyboardButton('Создать доску', callback_data='create_project')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, message.text, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, text=f'\nТЕБЕ СЮДА НЕЛЬЗЯ!!!\n\nНажми "/start"')


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
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Команда 1', callback_data='---')
                markup.add(item1)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\nТут будет инфа о командах',
                                      reply_markup=markup)

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



            # elif 'student_time' in call.data:
            #     markup = types.InlineKeyboardMarkup(row_width=6)
            #     flag = call.data.split('#')[1]
            #     if flag == '1':
            #         time = '10:00 - 14:00'
            #         item1 = [types.InlineKeyboardButton(f'{hour + 1}:00', callback_data=f'entry#{hour + 1}:00') for hour
            #                  in range(9, 13)]
            #         item2 = [types.InlineKeyboardButton(f'{hour + 1}:30', callback_data=f'entry#{hour + 1}:30') for hour
            #                  in range(9, 13)]
            #     elif flag == '2':
            #         time = '14:00 - 18:00'
            #         item1 = [types.InlineKeyboardButton(f'{hour + 1}:00', callback_data=f'entry#{hour + 1}:00') for hour
            #                  in range(13, 17)]
            #         item2 = [types.InlineKeyboardButton(f'{hour + 1}:30', callback_data=f'entry#{hour + 1}:30') for hour
            #                  in range(13, 17)]
            #     else:
            #         time = '18:00 - 22:00'
            #         item1 = [types.InlineKeyboardButton(f'{hour + 1}:00', callback_data=f'entry#{hour + 1}:00') for hour
            #                  in range(17, 21)]
            #         item2 = [types.InlineKeyboardButton(f'{hour + 1}:30', callback_data=f'entry#{hour + 1}:30') for hour
            #                  in range(17, 21)]
            #     item3 = types.InlineKeyboardButton('Назад', callback_data='sing_in')
            #     markup.add(*item1)
            #     markup.add(*item2)
            #     markup.add(item3)
            #     bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
            #                           text='\nВыбери удобное время',
            #                           parse_mode='Markdown', reply_markup=markup)
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
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Отправить', callback_data='---')
                markup.add(item1)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\nНапиши сообщение ПМу, он когда-нибудь ответит.',
                                      reply_markup=markup)

            elif call.data == 'project_info':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\nТвой проект: "Название"\n'
                                                                       'Команда: \n"участник 1"'
                                                                       '\n"участник 2"'
                                                                       '\n"участник 3"\n'
                                                                       'Ваш ПМ: "Егор"\n'
                                                                       'Созвон в такое-то время.')


    def handle(self, *args, **options):
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as error:
                print(error)
                time.sleep(5)


