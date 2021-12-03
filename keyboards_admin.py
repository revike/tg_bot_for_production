from datetime import datetime

import telebot

#  Admin keyboards operations
from constants import name_month_str


def key_admin():
    """Keyboard for administrator"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('🙎Сотрудники', '🛠Цехи')
    key.row('🔫Продукция', '💉Операции')
    key.row('📣Сообщить', '📃Отчеты')
    key.row('📚Справочник')
    return key


def key_admin_save():
    """Keyboard admin for save data"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('✅Сохранить', '🚫Отмена')
    return key


def key_admin_close(
        placeholder=None, data=None, workshop=False, product=False,
        instruction=False):
    """Keyboard admin for close operations"""
    key = telebot.types.ReplyKeyboardMarkup(
        True, input_field_placeholder=placeholder)
    if isinstance(data, list) and workshop:
        for workshop_data in data:
            key.row(workshop_data['name'].capitalize())
    if isinstance(data, list) and product:
        for product_data in data:
            key.row(product_data['product_name'].capitalize())
        if isinstance(data, list) and instruction:
            for instruction_data in data:
                key.row(instruction_data['instruction_name'].capitalize())
    if isinstance(data, str):
        key.row(data)
    key.row('🚫Отмена')
    return key


def key_admin_send():
    """Keyboard for send message"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('📨Отправить', '🚫Отмена')
    return key


# Employee
def key_admin_add_employee():
    """Keyboard admin for add new employee"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('📌Добавить сотрудника')
    key.row('⬅Назад')
    return key


def key_inline_employee():
    """Keyboard inline for button employee"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_employee',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🗑Уволить', callback_data='delete_employee',
    )
    key.row(key_button_edit, key_button_delete)
    return key


def key_inline_employee_active():
    """Keyboard inline for button employee is_active"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_employee',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🔄Восстановить', callback_data='active_employee',
    )
    key.row(key_button_edit, key_button_delete)
    return key


#  Workshop
def key_add_workshop():
    """Keyboard admin for add new employee"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('🏢Добавить новый цех')
    key.row('⬅Назад')
    return key


def key_inline_workshop():
    """Keyboard inline for button workshop"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_workshop',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🗑Удалить', callback_data='delete_workshop',
    )
    key.row(key_button_edit, key_button_delete)
    return key


def key_inline_workshop_active():
    """Keyboard inline for button workshop is active"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_workshop',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🔄Восстановить', callback_data='active_workshop',
    )
    key.row(key_button_edit, key_button_delete)
    return key


#  Products
def key_add_product():
    """Keyboard admin for add new employee"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('🔪Добавить новый продукт')
    key.row('⬅Назад')
    return key


def key_inline_product():
    """Keyboard inline for button product"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_product',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🗑Удалить', callback_data='delete_product',
    )
    key.row(key_button_edit, key_button_delete)
    return key


def key_inline_product_active():
    """Keyboard inline for button product is active"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_product',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🔄Восстановить', callback_data='active_product',
    )
    key.row(key_button_edit, key_button_delete)
    return key


#  Operation
def key_add_operation():
    """Keyboard admin for add new operation"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('💉Добавить операцию')
    key.row('🚫Отмена')
    return key


def key_see_operations():
    """Keyboard admin for see operations"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('💉Добавить операцию')
    key.row('🔭Показать все операции', '🔎Сортировать по товару')
    key.row('⬅Назад')
    return key


def key_inline_operation():
    """Keyboard inline for button operation"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_operation',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🗑Удалить', callback_data='delete_operation',
    )
    key.row(key_button_edit, key_button_delete)
    return key


def key_inline_operation_active():
    """Keyboard inline for button operation is active"""
    key = telebot.types.InlineKeyboardMarkup()
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_operation',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🔄Восстановить', callback_data='active_operation',
    )
    key.row(key_button_edit, key_button_delete)
    return key


# Report
def key_inline_report():
    """Keyboard inline for reports"""
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
        f'🔀{this_month} {this_year}', callback_data='report_this_month',
    )
    key_last_month = telebot.types.InlineKeyboardButton(
        f'↩{last_month} {this_year}', callback_data='report_last_month',
    )
    key_date_salary = telebot.types.InlineKeyboardButton(
        '📅Месяц/Год', callback_data='report_month_year'
    )
    key.row(key_last_month, key_this_month)
    key.row(key_date_salary)
    return key


# Instruction
def key_add_instruction():
    """Keyboard for add instruction"""
    key = telebot.types.ReplyKeyboardMarkup(True)
    key.row('📲Добавить инструкцию')
    key.row('🚫Отмена')
    return key


def key_inline_instruction(instruction):
    """Keyboard inline for button instruction"""
    key = telebot.types.InlineKeyboardMarkup()
    key_url = telebot.types.InlineKeyboardButton(
        f"👀{instruction['instruction_name']}",
        url=f"{instruction['url']}"
    )
    key_button_edit = telebot.types.InlineKeyboardButton(
        '✏Изменить', callback_data='edit_instruction',
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🗑Удалить', callback_data='delete_instruction',
    )
    key.row(key_url)
    key.row(key_button_edit, key_button_delete)
    return key


def key_inline_instruction_active(instruction):
    """Keyboard inline for button instruction is active"""
    key = telebot.types.InlineKeyboardMarkup()
    key_url = telebot.types.InlineKeyboardButton(
        f"👀{instruction['instruction_name']}",
        url=f"{instruction['url']}"
    )
    key_button_delete = telebot.types.InlineKeyboardButton(
        '🔄Восстановить', callback_data='active_instruction',
    )
    key.row(key_url)
    key.row(key_button_delete)
    return key
