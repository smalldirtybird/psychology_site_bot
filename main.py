import json
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


def send_main_menu_keyboard(bot, chat_id, course_content_folder):
    filepath = os.path.join(course_content_folder, 'main_header.txt')
    with open(filepath, 'r') as main_header_file:
        main_header = main_header_file.read()
    keyboard = [
        [InlineKeyboardButton('Для кого', callback_data='symptoms')],
        [InlineKeyboardButton('Программа', callback_data='program')],
        [InlineKeyboardButton('Преподаватели', callback_data='mentors')],
        [InlineKeyboardButton('Стоимость', callback_data='get_course')],
    ]
    bot.send_message(
        chat_id=chat_id,
        text=main_header,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def start(bot, update, course_content_folder):
    send_main_menu_keyboard(
        bot,
        update['message']['chat_id'],
        course_content_folder,
    )
    return 'HANDLE_MENU'


def send_program_info(bot, chat_id, course_content_folder):
    lessons_content_filepath = os.path.join(
        course_content_folder,
        'lessons.json',
    )
    with open(os.path.normpath(lessons_content_filepath), 'r') as lessons_json:
        lessons = json.load(lessons_json)
    keyboard = []
    for lesson, content in lessons.items():
        keyboard.append(
            [
                InlineKeyboardButton(
                    content['header'],
                    callback_data=lesson,
                )
            ]
        )
    keyboard.append([
            InlineKeyboardButton('В меню', callback_data='back_to_menu'),
            InlineKeyboardButton('О преподавателях', callback_data='mentors')
        ])
    filepath = os.path.join(course_content_folder, 'program_general_info.txt')
    with open(filepath, 'r') as program_general_info_file:
        program_general_info = program_general_info_file.read()
    bot.send_message(
        chat_id=chat_id,
        text=dedent(program_general_info),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def handle_symptoms(bot, update, course_content_folder):
    query = update.callback_query.data
    chat_id = update.callback_query['message']['chat_id']
    if query == 'back_to_menu':
        send_main_menu_keyboard(bot, chat_id, course_content_folder)
        return 'HANDLE_MENU'
    if query == 'program':
        send_program_info(bot, chat_id, course_content_folder)
        return 'HANDLE_PROGRAM'


def get_lessons_navigation_menu(query):
    query_number = int(query[-1])
    if query_number == 1:
        keyboard = [
            [
                InlineKeyboardButton(
                    '>',
                    callback_data=f'lesson_{query_number + 1}',
                )
            ]
        ]
    if query_number == 5:
        keyboard = [
            [
                InlineKeyboardButton(
                    '<',
                    callback_data=f'lesson_{query_number - 1}',
                )
            ]
        ]
    if query_number not in (1, 5):
        keyboard = [
            [
                InlineKeyboardButton(
                    '<',
                    callback_data=f'lesson_{query_number - 1}',
                ),
                InlineKeyboardButton(
                    '>',
                    callback_data=f'lesson_{query_number + 1}',
                )
            ]
        ]
    keyboard.append(
        [InlineKeyboardButton('Назад к программе', callback_data='program')])
    return keyboard


def send_mentors_menu(bot, chat_id, course_content_folder):
    lessons_content_filepath = os.path.join(
        course_content_folder,
        'mentors.json',
    )
    keyboard = []
    with open(os.path.normpath(lessons_content_filepath), 'r') as mentors_json:
        mentors = json.load(mentors_json)
        for mentor, content in mentors.items():
            keyboard.append(
                [InlineKeyboardButton(content['name'], callback_data=mentor)])
    keyboard.append(
        [InlineKeyboardButton('В меню', callback_data='back_to_menu')])
    filepath = os.path.join(course_content_folder, 'mentors_header.txt')
    with open(filepath, 'r') as mentors_header_file:
        mentors_header = mentors_header_file.read()
    bot.send_message(
        chat_id=chat_id,
        text=dedent(mentors_header),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def handle_program(bot, update, course_content_folder):
    query = update.callback_query.data
    chat_id = update.callback_query['message']['chat_id']
    lessons_content_filepath = os.path.join(
        course_content_folder, 'lessons.json')
    lessons_content = {}
    with open(os.path.normpath(lessons_content_filepath), 'r') as lessons_json:
        lessons = json.load(lessons_json)
        for lesson, content in lessons.items():
            lessons_content[lesson] =\
                f'{content["header"]}\n{content["content"]}'
    if query == 'back_to_menu':
        send_main_menu_keyboard(bot, chat_id, course_content_folder)
        return 'HANDLE_MENU'
    if query == 'mentors':
        send_mentors_menu(bot, chat_id, course_content_folder)
        return 'HANDLE_MENTORS'
    if query == 'program':
        send_program_info(bot, chat_id, course_content_folder)
        return 'HANDLE_PROGRAM'
    if query in lessons_content.keys():
        bot.send_message(
            chat_id=chat_id,
            text=dedent(lessons_content[query]),
            reply_markup=InlineKeyboardMarkup(
                get_lessons_navigation_menu(query))
        )
    return 'HANDLE_PROGRAM'


def handle_mentors(bot, update, course_content_folder):
    query = update.callback_query.data
    chat_id = update.callback_query['message']['chat_id']
    lessons_content_filepath = os.path.join(
        course_content_folder,
        'mentors.json',
    )
    mentors_content = {}
    with open(os.path.normpath(lessons_content_filepath), 'r') as mentors_json:
        mentors = json.load(mentors_json)
        for mentor, content in mentors.items():
            mentors_content[mentor] =\
                f'{content["name"]}\n{content["description"]}'
    if query == 'back_to_menu':
        send_main_menu_keyboard(bot, chat_id, course_content_folder)
        return 'HANDLE_MENU'
    if query == 'mentors':
        send_mentors_menu(bot, chat_id, course_content_folder)
    if query in mentors_content.keys():
        bot.send_message(
            chat_id=chat_id,
            text=dedent(mentors_content[query]),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Назад', callback_data='mentors')]])
        )
    return 'HANDLE_MENTORS'


def handle_payment(bot, update, course_content_folder):
    query = update.callback_query.data
    chat_id = update.callback_query['message']['chat_id']
    if query == 'back_to_menu':
        send_main_menu_keyboard(bot, chat_id, course_content_folder)
        return 'HANDLE_MENU'


def handle_menu(bot, update, course_content_folder):
    query = update.callback_query.data
    message_id = update.callback_query['message']['message_id']
    chat_id = update.callback_query['message']['chat_id']
    if query == 'symptoms':
        keyboard = [
            [
                InlineKeyboardButton('В меню', callback_data='back_to_menu'),
                InlineKeyboardButton('К программе', callback_data='program')
            ]
        ]
        filepath = os.path.join(course_content_folder, 'symptoms.txt')
        with open(filepath, 'r') as symptoms_file:
            symptoms = symptoms_file.read()
        bot.send_message(
            chat_id=chat_id,
            text=dedent(symptoms),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'HANDLE_SYMPTOMS'
    if query == 'program':
        send_program_info(bot, chat_id, course_content_folder)
        return 'HANDLE_PROGRAM'
    if query == 'mentors':
        send_mentors_menu(bot, chat_id, course_content_folder)
        return 'HANDLE_MENTORS'
    if query == 'get_course':
        bot.send_message(
            chat_id=chat_id,
            text=dedent("""
                Чтобы заказать курс, пожалуйста, пройдите по сслыке:
                https://kochet-psy.ru/anatomy_of_emotions
                """),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                'В меню', callback_data='back_to_menu')]]))
        return 'HANDLE_PAYMENT'
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    return 'START'


def handle_users_reply(bot, update, database_password, database_host,
                       database_port, image_filepath, course_content_folder):
    db = get_database_connection(
        database_password,
        database_host,
        database_port,
    )
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
        'START': partial(start, course_content_folder=course_content_folder),
        'HANDLE_MENU': partial(
            handle_menu,
            course_content_folder=course_content_folder,
        ),
        'HANDLE_SYMPTOMS': partial(
            handle_symptoms,
            course_content_folder=course_content_folder,
        ),
        'HANDLE_PROGRAM': partial(
            handle_program,
            course_content_folder=course_content_folder,
        ),
        'HANDLE_MENTORS': partial(
            handle_mentors,
            course_content_folder=course_content_folder,
        ),
        'HANDLE_PAYMENT': partial(
            handle_payment,
            course_content_folder=course_content_folder,
        ),
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(tg_user_id, next_state)


def main():
    load_dotenv()
    image_folder = os.environ['IMAGE_FOLDER_PATH']
    course_content_folder = os.environ['COURSE_CONTENT_PATH']
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
        course_content_folder=course_content_folder,
    )
    dispatcher.add_handler(CallbackQueryHandler(handling_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handling_users_reply))
    dispatcher.add_handler(CommandHandler('start', handling_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
