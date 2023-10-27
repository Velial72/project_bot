import os
from django.core.management.base import BaseCommand
import time
import telebot
from telebot import types
from dotenv import load_dotenv
from .trello import create_board, get_board_id, add_member


load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.InlineKeyboardMarkup(row_width=2)

        item1 = types.InlineKeyboardButton('Ученик', callback_data='student')
        item2 = types.InlineKeyboardButton('ПМ', callback_data='pm')
        markup.add(item1, item2)

        bot.send_message(message.chat.id, '\nПривет!\nСкажи кто ты?', reply_markup=markup)


    @bot.message_handler(content_types=['text'])
    def set_name_project(message):
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('Назад', callback_data='pm')
        item2 = types.InlineKeyboardButton('Создать проект', callback_data='create_project')
        markup.add(item1, item2)

        bot.send_message(message.chat.id, message.text, reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.message:
            if call.data == 'pm':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Изменить время', callback_data='change_time')
                item2 = types.InlineKeyboardButton('Инфа о командах', callback_data='team_info')
                item3 = types.InlineKeyboardButton('Создать доску', callback_data='trello')
                markup.add(item1, item2, item3)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text=f'\nЧто делаем?',
                                      reply_markup=markup)

            elif call.data == 'change_time':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('10:00 - 14:00', callback_data='time#1')
                item2 = types.InlineKeyboardButton('14:00 - 18:00', callback_data='time#2')
                item3 = types.InlineKeyboardButton('18:00 - 22:00', callback_data='time#3')
                item4 = types.InlineKeyboardButton('Назад', callback_data='pm')
                markup.add(item1, item2, item3, item4)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nКогда тебе удобно взять учеников?',
                                      parse_mode='Markdown', reply_markup=markup)

            elif 'time' in call.data:
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
                item2 = types.InlineKeyboardButton('Назад', callback_data='pm')
                markup.add(item1, item2)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\nТут будет инфа о командах',
                                      reply_markup=markup)

            elif call.data == 'trello':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Назад', callback_data='pm')
                markup.add(item1)

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\n Введите название проекта',
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

            elif call.data == 'student':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Связаться с ПМ', callback_data='message_to_pm')
                item2 = types.InlineKeyboardButton('Информация о проекте', callback_data='project_info')
                markup.add(item1, item2)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text=f'\nКакой у тебя вопрос?',
                                      reply_markup=markup)

            elif call.data == 'message_to_pm':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Отправить', callback_data='---')
                item2 = types.InlineKeyboardButton('Назад', callback_data='student')
                markup.add(item1, item2)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\nНапиши сообщение ПМу, он когда-нибудь ответит.',
                                      reply_markup=markup)

            elif call.data == 'project_info':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Назад', callback_data='student')
                markup.add(item1)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.id, text='\nТвой проект: "Название"\n'
                                                                       'Команда: \n"участник 1"'
                                                                       '\n"участник 2"'
                                                                       '\n"участник 3"\n'
                                                                       'Ваш ПМ: "Егор"\n'
                                                                       'Созвон в такое-то время.',
                                      reply_markup=markup)


    def handle(self, *args, **options):
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as error:
                print(error)
                time.sleep(5)

