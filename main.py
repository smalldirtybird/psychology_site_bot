import os
from functools import partial
from textwrap import dedent

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

database = None


def get_database_connection(database_password, database_host, database_port):
    global database
    if database is None:
        database = redis.Redis(
            host=database_host,
            port=database_port,
            password=database_password,
        )
    return database


def send_main_menu_keyboard(bot, chat_id):
    keyboard = [
        [InlineKeyboardButton('Для кого', callback_data='symptoms')],
        [InlineKeyboardButton('Программа', callback_data='program')],
        [InlineKeyboardButton('Преподаватели', callback_data='mentors')],
        [InlineKeyboardButton('Стоимость', callback_data='course_cost')],
    ]
    bot.send_message(
        chat_id=chat_id,
        text=dedent(
            """
            Анатомия стыда и вины.
            Способ справиться с негативными переживаниями.
            """),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def start(bot, update):
    send_main_menu_keyboard(bot, update['message']['chat_id'])
    return 'HANDLE_MENU'


def send_program_info(bot, update):
    keyboard = [
        [InlineKeyboardButton('Занятие 1. Введение', callback_data='lesson_1')],
        [InlineKeyboardButton('Занятие 2. Дезадаптивный стыд и вина', callback_data='lesson_2')],
        [InlineKeyboardButton('Занятие 3. Работа с чувством стыда', callback_data='lesson_3')],
        [InlineKeyboardButton('Занятие 4. Работа с чувством вины', callback_data='lesson_4')],
        [InlineKeyboardButton('Занятие 5. Бонусный урок «Эффективные извинения»', callback_data='lesson_5')],
        [
            InlineKeyboardButton('В меню', callback_data='back_to_menu'),
            InlineKeyboardButton('О преподавателях', callback_data='program')
        ]
    ]
    bot.send_message(
        chat_id=update.callback_query['message']['chat_id'],
        text=dedent("""
Курс состоит из 5 занятий в формате видео-лекций длительностью от 30 до 60 минут.

После каждого урока вы получите домашнее задание для практической отработки. В пакет курса включены специальные бланки и аудиозаписи для практической части.
        """),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def handle_symptoms(bot, update):
    query = update.callback_query.data
    message_id = update.callback_query['message']['message_id']
    chat_id = update.callback_query['message']['chat_id']
    if query == 'back_to_menu':
        send_main_menu_keyboard(bot, chat_id)
        return 'HANDLE_MENU'
    if query == 'program':
        send_program_info(bot, update)
        return 'HANDLE_PROGRAM'


def handle_program(bot, update):
    pass


def handle_menu(bot, update):
    query = update.callback_query.data
    message_id = update.callback_query['message']['message_id']
    chat_id = update.callback_query['message']['chat_id']
    if query == 'symptoms':
        keyboard = [
            [
                InlineKeyboardButton('В меню', callback_data='back_to_menu'),
                InlineKeyboardButton('К программе', callback_data='mentors')
            ]
        ]
        bot.send_message(
            chat_id=chat_id,
            text=dedent('''Последствия этих эмоций могут выражаться в:
        
- постоянном сравнении себя с другими, постоянной самокритике
- непокидающее фоновое ощущение собственной дефективности
- сниженная самооценка
- проблемы с границами, неумение сказать нет, взятие на себя чрезмерной ответсвенности за других
            
Если вы заметили, что один или больше пунктов про вас, и это в значительной мере ухудшает качество вашей жизни, данный курс может стать хорошим первым шагом для работы с эмоциями стыда и вины.
        
Данный курс построен на принципах доказательной психотерапии. Мы собрали материалы более 10 книги последних исследований в одном месте.

Вы узнаете, чем отличаются вина и стыд, откуда они взялись именно у вас, научитесь определять, когда они адаптивны, а когда нет. И самое главное - получите практические инструменты для самостоятельной работы с ними.         
        '''),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        print(query)
        return 'HANDLE_SYMPTOMS'
    if query == 'program':
        print(query)
        send_program_info(bot, update)
        return 'HANDLE_PROGRAM'
    if query == 'mentors':
        pass
    if query == 'course_cost':
        pass
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    return 'START'


def handle_users_reply(bot, update, database_password, database_host,
                       database_port, image_filepath):
    db = get_database_connection(
        database_password,
        database_host,
        database_port,
    )
    print(db.keys())
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    tg_user_id = f'tg_user_{chat_id}_state'
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(tg_user_id).decode('utf-8')
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_SYMPTOMS': handle_symptoms,
        'HANDLE_PROGRAM': handle_program,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(tg_user_id, next_state)


def main():
    load_dotenv()
    image_folder = os.environ['IMAGE_FOLDER_PATH']
    os.makedirs(image_folder, exist_ok=True)
    token = os.environ['TELEGRAM_BOT_TOKEN']
    updater = Updater(token)
    dispatcher = updater.dispatcher
    handling_users_reply = partial(
        handle_users_reply,
        database_password=os.environ['DB_PASSWORD'],
        database_host=os.environ['DB_HOST'],
        database_port=os.environ['DB_PORT'],
        image_filepath=image_folder,
    )
    dispatcher.add_handler(CallbackQueryHandler(handling_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handling_users_reply))
    dispatcher.add_handler(CommandHandler('start', handling_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
