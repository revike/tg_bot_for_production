from datetime import datetime

import telebot

from constants import name_month_str


def key_employee():
    """Keyboard open menu for employee"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('⌨Открыть меню')
    return key


def key_employee_start(work_active=False):
    """Keyboard for employee start"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    if work_active:
        key.row('🪚Закончить работу', '💶Зарплата')
    else:
        key.row('🪚Начать работу', '💶Зарплата')
    key.row('📚Справочник')
    return key


def key_employee_menu(keyboards=None):
    """Keyboard for employee menu"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('🚫Отмена')
    if keyboards:
        for keyboard in keyboards:
            try:
                key.row(keyboard['name'].capitalize())
            except KeyError:
                key.row(keyboard['product_name'].capitalize())
    return key


def key_employee_menu_operations(keyboards=None):
    """Keyboard for employee menu (operations)"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('🚫Отмена')
    if keyboards:
        for keyboard in keyboards:
            try:
                key.row(
                    f"`{keyboard['operation_name'].capitalize()}` - "
                    f"`{keyboard['price']}` руб/шт.")
            except KeyError:
                key.row('🚫Отмена')
    return key


def key_work_start():
    """Keyboard for start work"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('👌🏻Приступить', '🚫Отмена')
    return key


def key_employee_save():
    """Keyboard for save"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('✅Сохранить', '🚫Отмена')
    return key


def key_close():
    """Keyboard for close"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('🚫Отмена')
    return key


def key_inline_salary():
    """Keyboard inline salary"""
    date = datetime.now()
    this_month = date.month
    this_year = date.year
    last_month = this_month - 1
    if last_month == 0:
        last_month = 12
        this_year -= 1
    this_month = name_month_str()[this_month]
    last_month = name_month_str()[last_month]
    key = telebot.types.InlineKeyboardMarkup()
    key_this_month = telebot.types.InlineKeyboardButton(
        f'💴{this_month} {this_year}', callback_data='this_month',
    )
    key_last_month = telebot.types.InlineKeyboardButton(
        f'💶{last_month} {this_year}', callback_data='last_month',
    )
    key_today = telebot.types.InlineKeyboardButton(
        '💸Сегодня', callback_data='salary_today'
    )
    key_yesterday = telebot.types.InlineKeyboardButton(
        '💷Вчера', callback_data='salary_yesterday'
    )
    key.row(key_yesterday, key_today)
    key.row(key_last_month, key_this_month)
    return key


def key_inline_instruction_employee(instruction):
    """List instructions"""
    key = telebot.types.InlineKeyboardMarkup()
    key_url = telebot.types.InlineKeyboardButton(
        f"👀{instruction['instruction_name']}",
        url=f"{instruction['url']}"
    )
    key.row(key_url)
    return key
