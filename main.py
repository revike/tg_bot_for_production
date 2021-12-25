import os
import shutil
from datetime import datetime, timedelta

import pandas
import telebot
import validators

from constants import admin, token, name_month_str, name_month_int, orig_limit
from database import Database
from keyboards_admin import key_admin, key_inline_employee, \
    key_admin_add_employee, key_admin_close, key_inline_employee_active, \
    key_admin_save, key_inline_workshop, key_add_workshop, \
    key_inline_workshop_active, key_add_product, key_inline_product, \
    key_inline_product_active, key_inline_operation, key_add_operation, \
    key_inline_operation_active, key_admin_send, key_inline_report, \
    key_see_operations, key_add_instruction, key_inline_instruction, \
    key_inline_instruction_active
from keyboards_employee import key_employee, key_employee_menu, \
    key_employee_start, key_employee_menu_operations, key_work_start, \
    key_employee_save, key_close, key_inline_salary, \
    key_inline_instruction_employee, key_employee_id
from messages_admin import msg_employee_bad, \
    msg_workshop_list, msg_workshop_list_bad, msg_product_list, \
    msg_product_list_bad, msg_operation_list, msg_operation_list_bad, \
    msg_save_operation, msg_instruction_list, msg_instruction_list_bad
from messages_employee import msg_work_active, msg_work_end, msg_confirmation
from report import to_excel, one_file_excel

bot = telebot.TeleBot(token)
db = Database()
employee = {'number': ''}
workshop_data = {}
product_data = {}
operation_data = {'product_name': ''}
instruction_dict = {'id': '', 'url': ''}
work = {}


def run_bot():
    """Start bot"""
    bot.polling(none_stop=False)


@bot.message_handler(commands=['start', 'keyboard'])
def start_message(message):
    """Start command"""
    if message.from_user.id in admin:
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        if db.add_user(message.from_user.id):
            bot.send_message(message.from_user.id,
                             f'👇Отправьте ваш id своему руководителю👇',
                             reply_markup=key_employee())
            bot.send_message(message.from_user.id, f'{message.from_user.id}',
                             reply_markup=key_employee_id(
                                 message.from_user.id))
        else:
            bot.send_message(message.from_user.id, 'Главное меню❗',
                             reply_markup=key_employee())


@bot.message_handler(content_types=['text'])
def key_operation_admin(message):
    """Keyboard buttons"""
    if message.text == '🙎Сотрудники' and message.from_user.id in admin:
        i = 5
        len_profiles = db.len_profiles()
        if len_profiles < 6:
            i = 10
        for profile in db.get_profiles(i):
            id_ = profile['user_id']
            first_name, last_name = profile['first_name'], profile['last_name']
            number = profile['number']
            bot.send_contact(
                message.chat.id, number,
                f'{first_name.title()}',
                f'{last_name.title()} - `{id_}`',
                reply_markup=key_inline_employee(i))
            i -= 1
        bot.send_message(message.from_user.id,
                         '👇Добавить нового сотрудника👇',
                         reply_markup=key_admin_add_employee()
                         )

    elif message.text == '🛠Цехи' and message.from_user.id in admin:
        i = 5
        list_workshops = db.get_workshops(i)
        len_workshops = db.len_workshops()
        if len_workshops < 6:
            i = 10
        for workshop in list_workshops:
            msg = msg_workshop_list(workshop)
            bot.send_message(message.from_user.id, msg,
                             reply_markup=key_inline_workshop(i))
            i -= 1
        bot.send_message(message.from_user.id,
                         '👇Добавить новый цех👇',
                         reply_markup=key_add_workshop())

    elif message.text == '🔫Продукция' and message.from_user.id in admin:
        i = 5
        len_products = db.len_products()
        if len_products < 6:
            i = 10
        for product in db.get_products(i):
            msg = msg_product_list(product)
            bot.send_message(message.from_user.id, msg,
                             reply_markup=key_inline_product(i))
            i -= 1
        bot.send_message(message.from_user.id,
                         '👇Добавить новый продукт👇',
                         reply_markup=key_add_product())

    elif message.text == '💉Операции' and message.from_user.id in admin:
        bot.send_message(message.from_user.id,
                         '👇Добавить новую операцию👇',
                         reply_markup=key_see_operations())

    elif message.text == '🔎Сортировать по товару':
        operation_data['name'] = ''
        send = bot.send_message(message.from_user.id,
                                '👇По какому товару отсортировать?',
                                reply_markup=key_admin_close(
                                    operation_data['name'],
                                    db.get_products(limit=orig_limit),
                                    product=True
                                ))
        bot.register_next_step_handler(send, search_operations)

    elif message.text == '📣Сообщить' and message.from_user.id in admin:
        send = bot.send_message(message.from_user.id,
                                'Напишите объявление для всех сотрудников👇',
                                reply_markup=key_close())
        bot.register_next_step_handler(send, msg_for_employee)

    elif message.text == '📃Отчеты' and message.from_user.id in admin:
        bot.send_message(message.from_user.id, message.text,
                         reply_markup=key_inline_report())

    elif message.text == '📚Справочник' and message.from_user.id in admin:
        i = 5
        len_instruction = db.len_instructions()
        if len_instruction < 6:
            i = 10
        for instruction in db.get_instructions(i):
            msg = msg_instruction_list(instruction)
            bot.send_message(
                message.from_user.id, msg,
                reply_markup=key_inline_instruction(instruction, i))
            i -= 1
        bot.send_message(message.from_user.id, 'Добавить инструкцию👇',
                         reply_markup=key_add_instruction())
    elif message.text == '📲Добавить инструкцию' \
            and message.from_user.id in admin:
        send = bot.send_message(message.from_user.id,
                                'Введите название инструкции👇',
                                reply_markup=key_admin_close())
        bot.register_next_step_handler(send, add_instruction)

    elif message.text == '📌Добавить сотрудника' \
            and message.from_user.id in admin:
        employee['first_name'] = ''
        employee['last_name'] = ''
        employee['position'] = ''
        send = bot.send_message(message.from_user.id,
                                'Введите id сотрудника👇',
                                reply_markup=key_admin_close()
                                )
        bot.register_next_step_handler(send, add_employee)

    elif message.text == '🏢Добавить новый цех' and \
            message.from_user.id in admin:
        workshop_data['description'] = ''
        send = bot.send_message(message.from_user.id,
                                'Введите название цеха👇',
                                reply_markup=key_admin_close())
        bot.register_next_step_handler(send, add_workshop_name)

    elif message.text == '🔪Добавить новый продукт' \
            and message.from_user.id in admin:
        product_data['product_name'] = ''
        send = bot.send_message(message.from_user.id,
                                'Введите название продукта👇',
                                reply_markup=key_admin_close())
        bot.register_next_step_handler(send, add_product_name)

    elif message.text == '💉Добавить операцию' \
            and message.from_user.id in admin:
        operation_data['name'] = ''
        send = bot.send_message(message.from_user.id,
                                'К какому цеху относится операция? 👇',
                                reply_markup=key_admin_close(
                                    operation_data['name'],
                                    db.get_workshops(limit=orig_limit),
                                    workshop=True
                                ))
        bot.register_next_step_handler(send, add_operation_workshop)

    elif (message.text == '⬅Назад' and message.from_user.id in admin) or (
            message.text == '🚫Отмена' and message.from_user.id in admin):
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())

    #  Employee
    elif (message.text == '⬅Назад' and message.from_user.id not in admin) or (
            message.text == '🚫Отмена' and message.from_user.id not in admin):
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(False))

    elif message.from_user.id not in admin:
        if message.text == '⌨Открыть меню':
            try:
                profile_active = db.get_profile(message.from_user.id,
                                                is_active=True)
                if profile_active:
                    work_active = db.check_work_active(message.from_user.id)
                    bot.send_message(
                        message.from_user.id,
                        '⌨Пользуйтесь клавиатурой',
                        reply_markup=key_employee_start(work_active))
            except IndexError:
                bot.send_message(message.from_user.id,
                                 f'🥶Ваша учетная запись неактивна!\n'
                                 f'id - {message.from_user.id}',
                                 reply_markup=key_employee_id(
                                     message.from_user.id))

        elif message.text == '🪚Начать работу':
            if db.check_user(message.from_user.id):
                bot.send_message(message.from_user.id,
                                 f'🥶Ваша учетная запись неактивна\n'
                                 f'id - {message.from_user.id}',
                                 reply_markup=key_employee())
            else:
                work_active = db.check_work_active(message.from_user.id)
                if not work_active:
                    workshops = db.get_workshops(limit=orig_limit)
                    send = bot.send_message(message.from_user.id,
                                            'Выберите цех👇',
                                            reply_markup=key_employee_menu(
                                                workshops))
                    bot.register_next_step_handler(send, select_workshop)
                else:
                    bot.send_message(message.from_user.id,
                                     '🤌Сначала нужно закончить прошлое дело!',
                                     reply_markup=key_employee_start(
                                         work_active))

        elif message.text == '🪚Закончить работу':
            try:
                get_work = db.get_work(message.from_user.id)
                msg = msg_work_active(get_work)
                send = bot.send_message(message.from_user.id, msg,
                                        reply_markup=key_close())
                bot.register_next_step_handler(send, add_quantity)
            except IndexError:
                bot.send_message(message.from_user.id,
                                 '🆘 У вас не было начатой работы',
                                 reply_markup=key_employee_start(False))

        elif message.text == '💶Зарплата':
            bot.send_message(message.from_user.id,
                             '💶Зарплата', reply_markup=key_inline_salary())

        elif message.text == '📚Справочник':
            i = 5
            len_instructions = db.len_instructions()
            if len_instructions < 6:
                i = 10
            for instruction in db.get_instructions(i):
                msg = msg_instruction_list(instruction)
                bot.send_message(message.from_user.id, msg,
                                 reply_markup=key_inline_instruction_employee(
                                     instruction, i))
                i -= 1

        else:
            work_active = db.check_work_active(message.from_user.id)
            if db.check_user(message.from_user.id):
                key = key_employee()
            else:
                key = key_employee_start(work_active)
            bot.send_message(message.from_user.id,
                             'Пожалуйста, пользуйтесь кнопками👇',
                             reply_markup=key)

    else:
        bot.send_message(message.from_user.id,
                         '🤷Неверная операция\n'
                         'Пожалуйста, пользуйтесь кнопками👇',
                         reply_markup=key_admin())


def select_workshop(message):
    """Select workshop"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(False))
    else:
        try:
            if db.get_workshop(message.text.lower(), is_active=True):
                work['workshop'] = message.text.lower()
                products = db.get_products(limit=orig_limit)
                send = bot.send_message(message.from_user.id,
                                        'Выберите товар👇',
                                        reply_markup=key_employee_menu(
                                            products))
                bot.register_next_step_handler(send, select_product)
        except (IndexError, AttributeError):
            bot.send_message(message.from_user.id,
                             '❎Такого цеха не существует',
                             reply_markup=key_employee_start(False))


def select_product(message):
    """Select product"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(False))
    else:
        try:
            if db.get_product(message.text.lower(), is_active=True):
                work['product'] = message.text.lower()
                workshop = work['workshop']
                workshop_id = db.get_workshop(workshop, is_active=True)['id']
                product = work['product']
                product_id = db.get_product(product, is_active=True)['id']
                operations = db.get_operations_keyboard(workshop_id,
                                                        product_id)
                send = bot.send_message(
                    message.from_user.id,
                    'Выберите операцию👇',
                    reply_markup=key_employee_menu_operations(operations))
                bot.register_next_step_handler(send, select_operation,
                                               workshop_id=workshop_id,
                                               product_id=product_id)
        except (IndexError, AttributeError):
            bot.send_message(message.from_user.id,
                             '❎Такого продукта не существует',
                             reply_markup=key_employee_start(False))


def select_operation(message, workshop_id, product_id):
    """Select operation"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(False))
    else:
        try:
            message_data = message.text.lower().split('`')
            try:
                work['operation'] = message_data[1]
                work['price'] = message_data[3]
                if db.get_operation_check(
                        workshop_id, product_id, work['operation']):
                    msg = msg_confirmation(work)
                    send = bot.send_message(
                        message.from_user.id,
                        msg,
                        reply_markup=key_work_start())
                    bot.register_next_step_handler(send, work_start)
                else:
                    bot.send_message(message.from_user.id,
                                     '❎Такой операции не существует',
                                     reply_markup=key_employee_menu())
            except IndexError:
                bot.send_message(message.from_user.id,
                                 '❎Такой операции не существует',
                                 reply_markup=key_employee_start(False))
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_employee_start(False))


def work_start(message):
    """Work start"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(False))
    elif message.text == '👌🏻Приступить':
        if db.check_user(message.from_user.id):
            bot.send_message(message.from_user.id,
                             f'🥶Ваша учетная запись неактивна\n'
                             f'id - {message.from_user.id}',
                             reply_markup=key_employee())
        else:
            user_id = message.from_user.id
            workshop = work['workshop']
            product = work['product']
            operation = work['operation']
            price = work['price']
            db.add_work(user_id, workshop, product, operation, price,
                        active=True)
            msg = msg_work_end()
            work_active = db.check_work_active(message.from_user.id)
            bot.send_message(user_id, msg,
                             reply_markup=key_employee_start(work_active)
                             )
    else:
        bot.send_message(message.from_user.id,
                         'Пожалуйста, пользуйтесь кнопками👇',
                         reply_markup=key_employee_start(False)
                         )


def add_quantity(message):
    """Add quantity product"""
    if message.text == '🚫Отмена':
        work_active = db.check_work_active(message.from_user.id)
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(work_active))
    else:
        try:
            quantity = int(message.text)
            if quantity >= 0:
                get_work = db.get_work(message.from_user.id)
                msg = msg_work_active(get_work, quantity)
                send = bot.send_message(message.from_user.id, msg,
                                        reply_markup=key_employee_save())
                bot.register_next_step_handler(send, work_data_save,
                                               quantity=quantity)
            else:
                work_active = db.check_work_active(message.from_user.id)
                bot.send_message(message.from_user.id,
                                 '🆘 Неверное количество',
                                 reply_markup=key_employee_start(work_active))
        except (ValueError, TypeError):
            work_active = db.check_work_active(message.from_user.id)
            bot.send_message(message.from_user.id,
                             '🆘 Неверное количество',
                             reply_markup=key_employee_start(work_active))


def work_data_save(message, quantity):
    """Save data work in database"""
    if message.text == '🚫Отмена':
        work_active = db.check_work_active(message.from_user.id)
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_employee_start(work_active))
    elif message.text == '✅Сохранить':
        user_id = message.from_user.id
        get_work = db.get_work(user_id)
        workshop = get_work['w_workshop']
        product = get_work['w_product']
        operation = get_work['w_operation']
        price = get_work['w_price']
        db.add_work(user_id, workshop, product, operation, price,
                    active=False, quantity=quantity)
        if db.check_user(message.from_user.id):
            key = key_employee()
        else:
            key = key_employee_start(False)
        bot.send_message(message.from_user.id,
                         '✅Данные успешно добавлены',
                         reply_markup=key)
    else:
        work_active = db.check_work_active(message.from_user.id)
        bot.send_message(message.from_user.id,
                         '⌨Пользуйтесь клавиатурой',
                         reply_markup=key_employee_start(work_active))


def add_employee(message):
    """Add new employee"""
    global employee
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        user_id = message.text
        try:
            employee['user_id'] = int(user_id)

            if db.check_user(user_id):
                if db.check_old_user(user_id):
                    user = db.get_profile(user_id)
                    msg = msg_employee_bad(user)
                    bot.send_message(message.from_user.id, msg,
                                     reply_markup=key_inline_employee_active())
                elif db.check_user_register(user_id):
                    send = bot.send_message(message.from_user.id,
                                            'Введите имя сотрудника👇',
                                            reply_markup=key_admin_close()
                                            )
                    bot.register_next_step_handler(send, add_employee_name)
                else:
                    bot.send_message(message.from_user.id,
                                     '❎ Бот не знает такого id...',
                                     reply_markup=key_admin())
            else:
                bot.send_message(message.from_user.id,
                                 '❎ Такой пользователь уже существует',
                                 reply_markup=key_admin())
        except (ValueError, TypeError):
            bot.send_message(message.from_user.id,
                             '🆘Введен неверный id',
                             reply_markup=key_admin())
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_employee_name(message, edit=False):
    """Add name new employee"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        employee['first_name'] = ''.join(
            message.text.lower().split(' ')).strip()
        send = bot.send_message(message.from_user.id,
                                'Введите фамилию сотрудника👇',
                                reply_markup=key_admin_close(
                                    employee['last_name'],
                                    employee['last_name']
                                ))
        bot.register_next_step_handler(send, add_employee_first_name,
                                       edit=edit)
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_employee_first_name(message, edit=False):
    """Add new employee first name"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        employee['last_name'] = ''.join(
            message.text.lower().split(' ')).strip()
        send = bot.send_message(message.from_user.id,
                                'Введите должность сотрудника👇',
                                reply_markup=key_admin_close(
                                    employee['position'],
                                    employee['position']
                                ))
        bot.register_next_step_handler(send, add_employee_position, edit=edit)
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_employee_position(message, edit=False):
    """Add new employee position"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        employee['position'] = message.text.lower().strip()
        # send = bot.send_message(
        #     message.from_user.id,
        #     f"👤{employee['first_name']} {employee['last_name']}\n"
        #     f"🛠{employee['position']}\n✅Сохранить?",
        #     reply_markup=key_admin_save())
        # bot.register_next_step_handler(send, add_employee_bd)
        if not edit:
            employee['number'] = ''
        send = bot.send_message(message.from_user.id,
                                'Введите номер телефона сотрудника👇',
                                reply_markup=key_admin_close(
                                    employee['number'],
                                    employee['number']))
        bot.register_next_step_handler(send, add_employee_number)
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_employee_number(message):
    """Add number employee"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            if message.text[0] == '+':
                message.text = message.text.strip()[1:]
            if message.text[0] == '8':
                message.text = f'7{message.text.strip()[1:]}'
            message.text = ''.join(''.join(message.text.split(' ')).split('-'))
            message.text = int(message.text)
            employee['number'] = str(message.text)
            send = bot.send_message(
                message.from_user.id,
                f"👤{employee['first_name'].title()} "
                f"{employee['last_name'].title()}\n"
                f"🛠{employee['position'].title()}\n"
                f"📱{employee['number']}\n✅Сохранить?",
                reply_markup=key_admin_save())
            bot.register_next_step_handler(send, add_employee_bd)
        except (ValueError, TypeError):
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_employee_bd(message):
    """Add employee in database"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif message.text == '✅Сохранить':
        try:
            db.add_profile(
                employee['user_id'], employee['first_name'],
                employee['last_name'], employee['position'], employee['number']
            )
            bot.send_message(message.from_user.id,
                             '✅Данные успешно сохранены',
                             reply_markup=key_admin()
                             )
            bot.send_message(employee['user_id'],
                             '👌Ваша учетная запись добавлена или изменена')
        except IndexError:
            bot.send_message(message.from_user.id,
                             '❎Данные введены неверно!',
                             reply_markup=key_admin()
                             )
    else:
        bot.send_message(message.from_user.id,
                         '🤷Неверная операция\n'
                         'Пожалуйста, пользуйтесь кнопками👇',
                         reply_markup=key_admin())


def add_workshop_name(message, edit=False, workshop_name=None):
    """Add workshop name"""
    global workshop_data
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            name = message.text.lower().strip()
            workshop_data['name'] = name
            if db.check_workshop(name, edit=edit):
                if db.check_old_workshop(name):
                    workshop = db.get_workshop(name)
                    msg = msg_workshop_list_bad(workshop)
                    bot.send_message(message.from_user.id, msg,
                                     reply_markup=key_inline_workshop_active())
                else:
                    if name in db.get_workshops_active(workshop_name):
                        bot.send_message(message.from_user.id,
                                         '❎ Такой цех уже существует',
                                         reply_markup=key_admin())
                    else:
                        send = bot.send_message(message.from_user.id,
                                                'Введите описание цеха👇',
                                                reply_markup=key_admin_close(
                                                    workshop_data[
                                                        'description'],
                                                    workshop_data[
                                                        'description']))
                        bot.register_next_step_handler(send, add_workshop_desc)
            else:
                bot.send_message(message.from_user.id,
                                 '❎ Такой цех уже существует',
                                 reply_markup=key_admin())
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_workshop_desc(message):
    """Add workshop description"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        workshop_data['description'] = message.text.strip()
        send = bot.send_message(message.from_user.id,
                                f"🏪{workshop_data['name']}\n"
                                f"📄{workshop_data['description']}\n"
                                f"✅Сохранить?",
                                reply_markup=key_admin_save())
        bot.register_next_step_handler(send, add_workshop_bd)
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_workshop_bd(message):
    """Add workshop in database"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif message.text == '✅Сохранить':
        try:
            id_ = workshop_data['id']
            db.edit_workshop(id_, workshop_data['name'],
                             workshop_data['description'])
        except KeyError:
            db.add_workshop(
                workshop_data['name'], workshop_data['description']
            )
        bot.send_message(message.from_user.id,
                         '✅Данные успешно сохранены',
                         reply_markup=key_admin()
                         )
    else:
        bot.send_message(message.from_user.id,
                         '🤷Неверная операция\n'
                         'Пожалуйста, пользуйтесь кнопками👇',
                         reply_markup=key_admin())


def add_product_name(message, edit=False, old_product_name=None):
    """Add product name"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            product_data['product_name'] = message.text.lower().strip()
            if db.check_product(product_data['product_name'], edit=edit):
                if db.check_old_product(product_data['product_name']):
                    product = db.get_product(product_data['product_name'])
                    msg = msg_product_list_bad(product)
                    bot.send_message(message.from_user.id, msg,
                                     reply_markup=key_inline_product_active())
                else:
                    if product_data['product_name'] in db.get_products_active(
                            old_product_name):
                        bot.send_message(message.from_user.id,
                                         '❎ Такой продукт уже существует',
                                         reply_markup=key_admin())
                    else:
                        send = bot.send_message(
                            message.from_user.id,
                            f"🎠{product_data['product_name']}\n"
                            f"✅Сохранить?",
                            reply_markup=key_admin_save())
                        bot.register_next_step_handler(send, add_product_db,
                                                       edit=edit)
            else:
                bot.send_message(message.from_user.id,
                                 '❎ Такой продукт уже существует',
                                 reply_markup=key_admin())
        except (AttributeError, IndexError):
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_product_db(message, edit=False):
    """Add product in database"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif message.text == '✅Сохранить':
        try:
            db.add_product(product_data['id'], product_data['product_name'],
                           edit=edit)
        except KeyError:
            product_data['id'] = ''
            db.add_product(product_data['id'], product_data['product_name'],
                           edit=edit)
        bot.send_message(message.from_user.id,
                         '✅Данные успешно сохранены',
                         reply_markup=key_admin()
                         )
    else:
        bot.send_message(message.from_user.id,
                         '🤷Неверная операция\n'
                         'Пожалуйста, пользуйтесь кнопками👇',
                         reply_markup=key_admin())


def search_operations(message):
    """Sorting operations (products)"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            product = message.text.split('`')[0].lower()
            i = 5
            search_operations = db.search_operations(product, limit=i)
            if search_operations:
                for operation in search_operations:
                    msg = msg_operation_list(operation)
                    bot.send_message(message.from_user.id, msg,
                                     reply_markup=key_inline_operation(i))
                    i -= 1
                bot.send_message(message.from_user.id,
                                 f'👆Операции для - {product.title()}',
                                 reply_markup=key_see_operations())
            else:
                bot.send_message(message.from_user.id,
                                 '🤷У такого продукта нет операций',
                                 reply_markup=key_see_operations())
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_see_operations())


def add_operation_workshop(message, edit=False, old_operation=False):
    """Add workshop for operation"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            if db.check_workshop(message.text.lower()):
                bot.send_message(message.from_user.id,
                                 '💁Такого цеха не существует!',
                                 reply_markup=key_admin())
            else:
                operation_data['name'] = message.text.lower()

                send = bot.send_message(
                    message.from_user.id,
                    'К какому продукту относится операция? 👇',
                    reply_markup=key_admin_close(
                        placeholder=operation_data[
                            'product_name'],
                        data=db.get_products(limit=orig_limit),
                        product=True
                    ))
                bot.register_next_step_handler(
                    send, add_operation_product, edit=edit,
                    old_operation=old_operation)
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_operation_product(message, edit=False, old_operation=False):
    """Add product for operation"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            if db.check_product(message.text.lower()):
                bot.send_message(message.from_user.id,
                                 '💁Такого продукта не существует!',
                                 reply_markup=key_admin())
            else:
                operation_data['product_name'] = message.text.lower()
                if edit:
                    placeholder = operation_data['operation_name']
                else:
                    placeholder = None
                send = bot.send_message(message.from_user.id,
                                        'Введите название операции 👇',
                                        reply_markup=key_admin_close(
                                            placeholder=placeholder,
                                            data=placeholder,
                                        ))
                bot.register_next_step_handler(send, add_operation_name,
                                               edit=edit,
                                               old_operation=old_operation)
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_operation_name(message, edit=False, old_operation=False):
    """Add name for operations"""
    global operation_data
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            operation_name = message.text.lower().strip()
            operation_data['operation_name'] = operation_name
            name = operation_data['name'].lower()
            try:
                name_workshop_id = db.get_workshop(name)['id']
            except IndexError:
                name_workshop_id = db.get_workshop(name, is_active=True)['id']
            product_name = operation_data['product_name'].lower()
            try:
                product_name_id = db.get_product(product_name)['id']
            except IndexError:
                product_name_id = db.get_product(product_name, is_active=True)[
                    'id']
            if db.check_operation(
                    operation_name, name_workshop_id, product_name_id,
                    edit=edit):
                if db.check_old_operation(
                        operation_name, name_workshop_id, product_name_id):
                    operation = db.get_operation_name(
                        operation_name, name_workshop_id, product_name_id)
                    msg = msg_operation_list_bad(operation)
                    bot.send_message(
                        message.from_user.id, msg,
                        reply_markup=key_inline_operation_active())
                else:
                    new_operation = {operation_name: [
                        name, product_name
                    ]}
                    if new_operation in db.get_operation_active(old_operation):
                        bot.send_message(message.from_user.id,
                                         '❎ Такая операция уже существует',
                                         reply_markup=key_admin())
                    else:
                        try:
                            if edit:
                                placeholder = str(operation_data['price'])
                            else:
                                placeholder = None
                        except KeyError:
                            placeholder = None
                        send = bot.send_message(message.from_user.id,
                                                'Какая стоимость операции? 👇',
                                                reply_markup=key_admin_close(
                                                    placeholder,
                                                    placeholder))
                        bot.register_next_step_handler(send,
                                                       add_operation_price,
                                                       edit=edit)
            else:
                bot.send_message(message.from_user.id,
                                 '❎ Такая операция уже существует',
                                 reply_markup=key_admin())
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_operation_price(message, edit=False):
    """Add price for operation"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            price = float(message.text.replace(',', '.').replace(' ', ''))
            if price > 0:
                operation_data['price'] = price
                msg = msg_save_operation(operation_data)
                send = bot.send_message(message.from_user.id, msg,
                                        reply_markup=key_admin_save())
                bot.register_next_step_handler(send, add_operation_db,
                                               edit=edit)
            else:
                bot.send_message(message.from_user.id,
                                 '🆘 Неверная стоимость',
                                 reply_markup=key_admin())
        except (ValueError, AttributeError):
            bot.send_message(message.from_user.id,
                             '❌ Цена введена неправильно!',
                             reply_markup=key_admin())


def add_operation_db(message, edit=False):
    """Add operation in database"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif message.text == '✅Сохранить':
        name = operation_data['name'].lower()
        try:
            workshop_id = db.get_workshop(name)['id']
        except IndexError:
            workshop_id = db.get_workshop(name, is_active=True)['id']
        product_name = operation_data['product_name'].lower()
        try:
            product_id = db.get_product(product_name)['id']
        except IndexError:
            product_id = db.get_product(product_name, is_active=True)['id']
        try:
            db.add_operation(
                operation_data['id'], operation_data['operation_name'],
                workshop_id, product_id,
                operation_data['price'], edit=edit)
        except KeyError:
            operation_data['id'] = ''
            db.add_operation(
                operation_data['id'], operation_data['operation_name'],
                workshop_id, product_id,
                operation_data['price'], edit=edit)
        bot.send_message(message.from_user.id,
                         '✅Данные успешно сохранены',
                         reply_markup=key_admin()
                         )
    else:
        bot.send_message(message.from_user.id,
                         '🤷Неверная операция\n'
                         'Пожалуйста, пользуйтесь кнопками👇',
                         reply_markup=key_admin())


def msg_for_employee(message):
    """Print message for employee"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        send = bot.send_message(message.from_user.id,
                                f"📬Отправить сообщение?\n"
                                f"Текст: {message.text}",
                                reply_markup=key_admin_send())
        bot.register_next_step_handler(send, send_message, msg=message.text)
    else:
        bot.send_message(message.from_user.id,
                         '🧐Объявление должно состоять только из текста!',
                         reply_markup=key_admin())


def send_message(message, msg):
    """Send message for employee"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif message.text == '📨Отправить':
        users = db.get_profiles(limit=orig_limit)
        for user in users:
            bot.send_message(user['user_id'], f"⭕Объявление:\n{msg}")
        bot.send_message(message.from_user.id, '✅Рассылка отправлена',
                         reply_markup=key_admin())
    else:
        bot.send_message(message.from_user.id, '🚯Сообщение не отправлено',
                         reply_markup=key_admin())


def main_report(message):
    """Main report"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    else:
        try:
            date = message.text.split('.')
            try:
                year_now = datetime.now().year
                month, year = int(date[0]), int(date[1])
                if (0 < month < 13) and (2015 < year <= year_now) and len(
                        date) == 2:
                    data_dict = {
                        'Продукт': [], 'Операция': [], 'Цех': [], 'Цена': [],
                        'Количество': []
                    }
                    month = name_month_str()[month]
                    data_user_and_salary = [['Сотрудник'],
                                            ['Должность'],
                                            ['Тел:'],
                                            [f'Зарплата за {month} {year} г.']]
                    users = db.get_profiles(limit=orig_limit)
                    if users:
                        data_list_read = []
                        data_sheet_name = []
                        for user in users:
                            month = name_month_int()[month]
                            data = db.get_work_data(user['user_id'], month,
                                                    year)
                            last_first_name = \
                                f"{user['first_name'].title()} " \
                                f"{user['last_name'].title()}"
                            data_user_and_salary[0].append(last_first_name)
                            for report in data:
                                data_dict['Продукт'].append(
                                    report['w_product'])
                                data_dict['Операция'].append(
                                    report['w_operation'])
                                data_dict['Цех'].append(report['w_workshop'])
                                data_dict['Цена'].append(report['w_price'])
                                data_dict['Количество'].append(
                                    report['w_quantity'])
                            user_salary = 0
                            i = len(data_dict['Цена'])
                            while i > 0:
                                user_salary += data_dict['Цена'][i - 1] * \
                                               data_dict['Количество'][i - 1]
                                i -= 1
                            data_user_and_salary[3].append(user_salary)
                            data_user_and_salary[1].append(user['position'])
                            data_user_and_salary[2].append(user['number'])
                            month = name_month_str()[month]
                            file = f"{last_first_name} - {month} {year} - {user['user_id']}"
                            to_excel(data_dict, data_user_and_salary, file)
                            data_dict = {
                                'Продукт': [], 'Операция': [], 'Цех': [],
                                'Цена': [],
                                'Количество': []
                            }
                            data_user_and_salary = [['Сотрудник'],
                                                    ['Должность'],
                                                    ['Тел:'],
                                                    [
                                                        f'Зарплата за {month} {year} г.']]
                            read_file = pandas.read_excel(
                                f'reports/{file}.xlsx')
                            data_list_read.append(read_file)
                            data_sheet_name.append(
                                ''.join(last_first_name.split(' ')))
                        one_file_excel(f'{month} {year}', data_sheet_name,
                                       data_list_read)
                        shutil.make_archive(
                            f'report_zip/Отчеты-{month}-{year}', 'zip',
                            'reports')
                        bot.send_document(
                            message.from_user.id,
                            open(f'report_zip/Отчеты-{month}-{year}.zip',
                                 'rb', ))
                        bot.send_message(
                            message.from_user.id,
                            f'👆Отчеты за {month.lower()} {year} г. 👆',
                            reply_markup=key_admin())
                        file_list = [f for f in os.listdir('reports') if
                                     f.endswith(".xlsx")]
                        for f in file_list:
                            os.remove(os.path.join('reports', f))
                        file_list = [f for f in os.listdir('report_zip') if
                                     f.endswith(".zip")]
                        for f in file_list:
                            os.remove(os.path.join('report_zip', f))
                    else:
                        bot.send_message(message.from_user.id,
                                         '🤷В базе еще нет сотрудников',
                                         reply_markup=key_admin())
                else:
                    bot.send_message(message.from_user.id,
                                     '🤷Неверная дата',
                                     reply_markup=key_admin())
            except (ValueError, IndexError):
                bot.send_message(message.from_user.id,
                                 '🤷Неверная дата',
                                 reply_markup=key_admin())
        except AttributeError:
            bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                             reply_markup=key_admin())


def add_instruction(message, edit=False, old_instruction_dict=None):
    """Add name instruction"""
    global instruction_dict
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        if db.check_instruction_name(message.text.lower().strip()) or edit:
            instruction_dict['instruction_name'] = message.text.lower().strip()
            if not edit:
                instruction_dict['url'] = ''
                key = key_admin_close(instruction_dict['url'],
                                      instruction_dict['url'])
            else:
                key = key_admin_close(old_instruction_dict['url'],
                                      old_instruction_dict['url'])
            send = bot.send_message(message.from_user.id,
                                    'Введите ссылку👇',
                                    reply_markup=key)
            bot.register_next_step_handler(
                send, add_instruction_link, edit,
                old_instruction_dict=old_instruction_dict)
        else:
            bot.send_message(message.from_user.id,
                             '❎Инструкция с таким названием уже есть',
                             reply_markup=key_add_instruction())
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_instruction_link(message, edit=False, old_instruction_dict=None):
    """Add link instruction"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif isinstance(message.text, str):
        if message.text[-1] != '/':
            message.text += '/'
        try:
            link = message.text.split('//')[1]
        except:
            link = message.text.split('//')[0]
        message.text = f'http://{link}'
        if validators.url(message.text):
            if db.check_instruction_url(message.text) or edit:
                if db.check_instruction_url(message.text):
                    try:
                        instruction = db.get_instruction(message.text)
                        msg = msg_instruction_list_bad(instruction)
                        bot.send_message(
                            message.from_user.id, msg,
                            reply_markup=key_inline_instruction_active(
                                instruction))
                    except IndexError:
                        instruction_dict['url'] = message.text
                        send = bot.send_message(
                            message.from_user.id,
                            f"✅Сохранить инструкцию "
                            f"`{instruction_dict['instruction_name']}`?",
                            reply_markup=key_admin_save()
                        )
                        bot.register_next_step_handler(
                            send, add_instruction_db, edit,
                            old_instruction_dict=old_instruction_dict)
                else:
                    instruction_dict['url'] = message.text
                    send = bot.send_message(
                        message.from_user.id,
                        f"✅Сохранить инструкцию "
                        f"`{instruction_dict['instruction_name']}`?",
                        reply_markup=key_admin_save()
                    )
                    bot.register_next_step_handler(
                        send, add_instruction_db, edit,
                        old_instruction_dict=old_instruction_dict)
            else:
                bot.send_message(message.from_user.id,
                                 '❎Ссылка на эту инструкцию уже есть',
                                 reply_markup=key_add_instruction())
        else:
            bot.send_message(message.from_user.id, '🔐Неверная ссылка',
                             reply_markup=key_admin())
    else:
        bot.send_message(message.from_user.id, '🤖Что-то пошло не так!',
                         reply_markup=key_admin())


def add_instruction_db(message, edit=False, old_instruction_dict=None):
    """Add instruction in database"""
    if message.text == '🚫Отмена':
        bot.send_message(message.from_user.id, 'Главное меню❗',
                         reply_markup=key_admin())
    elif message.text == '✅Сохранить':
        if edit:
            old_url = old_instruction_dict['url']
        else:
            old_url, old_instruction_name = False, False

        instruction_name = instruction_dict['instruction_name']
        url = instruction_dict['url']

        if not db.check_instruction_url(url, is_active=True) and edit:
            db.instruction_edit_name(old_url=old_url,
                                     instruction_name=instruction_name)
            if old_instruction_dict['instruction_name'] != instruction_dict[
                'instruction_name']:
                bot.send_message(
                    message.from_user.id,
                    f"✅ У инструкции `{old_instruction_dict['instruction_name']}` "
                    f"изменено только имя на "
                    f"`{instruction_dict['instruction_name']}`!\n"
                    f"Ссылки дублировать нельзя!", reply_markup=key_admin())
            else:
                bot.send_message(
                    message.from_user.id,
                    f"✅ Инструкция `{instruction_dict['instruction_name']}` "
                    f"успешно сохранена", reply_markup=key_admin())
        else:
            db.add_instruction(
                old_url=old_url,
                instruction_name=instruction_name, url=url, edit=edit)
            bot.send_message(
                message.from_user.id,
                f"✅ Инструкция `{instruction_dict['instruction_name']}` "
                f"успешно сохранена", reply_markup=key_admin())
    else:
        bot.send_message(message.from_user.id,
                         '🚫Инструкция не сохранена',
                         reply_markup=key_admin())


@bot.callback_query_handler(func=lambda call: True)
def key_inline_operations(message):
    """Command for key inline"""
    if message.data == 'edit_workshop':
        bot.clear_step_handler_by_chat_id(message.message.chat.id)
        name = message.message.text.split("`")[1].lower()
        try:
            workshop = db.get_workshop(name)
        except IndexError:
            workshop = db.get_workshop(name, is_active=True)
        workshop_data['id'] = workshop['id']
        workshop_data['name'] = workshop['name']
        workshop_data['description'] = workshop['description']
        bot.answer_callback_query(message.id)
        send = bot.send_message(message.message.chat.id,
                                'Введите название цеха👇',
                                reply_markup=key_admin_close(
                                    workshop_data['name'],
                                    workshop_data['name']))
        bot.register_next_step_handler(send, add_workshop_name, edit=True,
                                       workshop_name=workshop_data['name'])
    if message.data == 'delete_workshop':
        name = message.message.text.split("`")[1].lower()
        if db.del_workshop(name):
            bot.answer_callback_query(message.id,
                                      text='Цех удален!',
                                      cache_time=1)
            workshop = db.get_workshop(name)
            msg = msg_workshop_list_bad(workshop)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_workshop_active())
        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'active_workshop':
        name = message.message.text.split("`")[1].lower()
        if db.recovery_workshop(name):
            workshop = db.get_workshop(name, is_active=True)
            msg = msg_workshop_list(workshop)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_workshop(1))
            bot.answer_callback_query(message.id,
                                      text='Цех восстановлен!',
                                      cache_time=1)

        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'yet_workshop':
        i = 5
        name = message.message.text.split("`")[1].lower()
        try:
            yet = db.get_workshop(name, is_active=True)['id']
        except IndexError:
            yet = db.get_workshop(name)['id']
            bot.answer_callback_query(
                message.id,
                '🤖Я не знаю кто следующий, потому что этот цех '
                'удален...\n🤪Лайфхак: Удали и сразу '
                'восстанови предыдущую запись!')
        bot.edit_message_reply_markup(message.message.chat.id,
                                      message.message.message_id,
                                      reply_markup=key_inline_workshop(0))
        workshops_list = db.get_workshops(i, yet=yet, next=False)
        workshops_list_id = []
        for workshop in workshops_list:
            workshops_list_id.append(workshop['id'])
        if len(workshops_list_id) == 0:
            i = 10
            bot.answer_callback_query(message.id, 'Это последний цех в '
                                                  'списке')
        if len(workshops_list_id) >= 5:
            workshops_list_id = workshops_list_id[:5]
        for workshop in db.get_workshops(list_id=workshops_list_id, next=True,
                                         limit=5, yet=yet):
            msg = msg_workshop_list(workshop)
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id, msg,
                             reply_markup=key_inline_workshop(i))
            i -= 1

    if message.data == 'edit_employee':
        bot.clear_step_handler_by_chat_id(message.message.chat.id)
        global employee
        try:
            user_id = message.message.text.split('`')[1]
        except AttributeError:
            user_id = message.message.contact.last_name.split('`')[1]
        try:
            user = db.get_profile(user_id)
        except IndexError:
            user = db.get_profile(user_id, is_active=True)
        employee['user_id'] = user_id
        employee['first_name'] = user['first_name']
        employee['last_name'] = user['last_name']
        employee['position'] = user['position']
        bot.answer_callback_query(message.id)
        send = bot.send_message(message.message.chat.id,
                                'Введите имя сотрудника👇',
                                reply_markup=key_admin_close(
                                    employee['first_name'],
                                    employee['first_name']))
        bot.register_next_step_handler(send, add_employee_name, edit=True)
    if message.data == 'delete_employee':
        try:
            user_id = message.message.text.split('`')[1]
        except AttributeError:
            user_id = message.message.contact.last_name.split('`')[1]
        try:
            user = db.get_profile(user_id)
        except IndexError:
            user = db.get_profile(user_id, is_active=True)
        if db.del_profile(user['user_id']):
            bot.edit_message_reply_markup(
                message.message.chat.id,
                message.message.message_id,
                reply_markup=key_inline_employee_active())
            bot.answer_callback_query(message.id,
                                      text='Сотрудник уволен!',
                                      cache_time=1)
        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'active_employee':
        try:
            user_id = message.message.text.split('`')[1]
        except AttributeError:
            user_id = message.message.contact.last_name.split('`')[1]
        if db.recovery_profile(user_id):
            bot.edit_message_reply_markup(
                message.message.chat.id,
                message.message.message_id,
                reply_markup=key_inline_employee(1)
            )
            bot.answer_callback_query(message.id,
                                      text='Сотрудник восстановлен!',
                                      cache_time=1)

        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'yet_employee':
        i = 5
        try:
            user_id = message.message.text.split('`')[1]
        except AttributeError:
            user_id = message.message.contact.last_name.split('`')[1]
        try:
            yet = db.get_profile(user_id, is_active=True)['id']
        except IndexError:
            yet = db.get_profile(user_id)['id']
            bot.answer_callback_query(
                message.id,
                '🤖Я не знаю кто следующий, потому что этот сотрудник '
                'удален...\n🤪Лайфхак: Удали и сразу '
                'восстанови предыдущую запись!')
        bot.edit_message_reply_markup(message.message.chat.id,
                                      message.message.message_id,
                                      reply_markup=key_inline_employee(0))
        employee_list = db.get_profiles(i, yet=yet, next=False)
        employee_list_id = []
        for employee in employee_list:
            employee_list_id.append(employee['id'])
        if len(employee_list_id) == 0:
            i = 10
            bot.answer_callback_query(message.id, 'Это последний сотрудник в '
                                                  'списке')
        if len(employee_list_id) >= 5:
            employee_list_id = employee_list_id[:5]
        for employee in db.get_profiles(list_id=employee_list_id, next=True,
                                        limit=i, yet=yet):
            id_ = employee['user_id']
            first_name, last_name = employee['first_name'], employee[
                'last_name']
            number = employee['number']
            bot.answer_callback_query(message.id)
            bot.send_contact(
                message.message.chat.id, number,
                f'{first_name.title()}',
                f'{last_name.title()} - `{id_}`', reply_markup=key_inline_employee(i))
            i -= 1

    if message.data == 'edit_product':
        bot.clear_step_handler_by_chat_id(message.message.chat.id)
        product_name = message.message.text.split("`")[1].lower()
        try:
            product = db.get_product(product_name)
        except IndexError:
            product = db.get_product(product_name, is_active=True)
        product_data['id'] = product['id']
        product_data['product_name'] = product['product_name']
        bot.answer_callback_query(message.id)
        send = bot.send_message(message.message.chat.id,
                                'Введите название продукта👇',
                                reply_markup=key_admin_close(
                                    product_data['product_name'],
                                    product_data['product_name']))
        bot.register_next_step_handler(send, add_product_name, edit=True,
                                       old_product_name=product_data[
                                           'product_name'])
    if message.data == 'delete_product':
        product_name = message.message.text.split("`")[1].lower()
        if db.del_product(product_name):
            bot.answer_callback_query(message.id,
                                      text='Продукт удален!',
                                      cache_time=1)
            product = db.get_product(product_name)
            msg = msg_product_list_bad(product)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_product_active())
        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'active_product':
        product_name = message.message.text.split("`")[1].lower()
        if db.recovery_product(product_name):
            product = db.get_product(product_name, is_active=True)
            msg = msg_product_list(product)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_product(1))
            bot.answer_callback_query(message.id,
                                      text='Продукт восстановлен!',
                                      cache_time=1)

        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'yet_product':
        i = 5
        product_name = message.message.text.split("`")[1].lower()
        try:
            yet = db.get_product(product_name, is_active=True)['id']
        except IndexError:
            yet = db.get_product(product_name)['id']
            bot.answer_callback_query(
                message.id,
                '🤖Я не знаю кто следующий, потому что этот продукт '
                'удален...\n🤪Лайфхак: Удали и сразу '
                'восстанови предыдущую запись!')
        bot.edit_message_reply_markup(message.message.chat.id,
                                      message.message.message_id,
                                      reply_markup=key_inline_product(0))
        product_list = db.get_products(i, yet=yet, next=False)
        product_list_id = []
        for product in product_list:
            product_list_id.append(product['id'])
        if len(product_list_id) == 0:
            i = 10
            bot.answer_callback_query(message.id, 'Это последний продукт в '
                                                  'списке')
        if len(product_list_id) >= 5:
            product_list_id = product_list_id[:5]
        for product in db.get_products(yet=yet, list_id=product_list_id,
                                       next=True, limit=i):
            msg = msg_product_list(product)
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id, msg,
                             reply_markup=key_inline_product(i))
            i -= 1

    if message.data == 'edit_operation':
        bot.clear_step_handler_by_chat_id(message.message.chat.id)
        id_ = message.message.text.split("`")[1]
        try:
            operation = db.get_operation(id_)
        except IndexError:
            operation = db.get_operation(id_, is_active=True)
        operation_data['id'] = operation['id']
        operation_data['operation_name'] = operation['operation_name']
        operation_data['name'] = operation['name']
        operation_data['product_name'] = operation['product_name']
        operation_data['price'] = operation['price']
        bot.answer_callback_query(message.id)
        send = bot.send_message(message.message.chat.id,
                                'К какому цеху относится операция? 👇',
                                reply_markup=key_admin_close(
                                    operation_data['name'],
                                    db.get_workshops(limit=orig_limit),
                                    workshop=True)
                                )
        old_operation = {operation_data['operation_name']: [
            operation_data['name'], operation_data['product_name']
        ]}
        bot.register_next_step_handler(
            send, add_operation_workshop,
            old_operation=old_operation, edit=True
        )
    if message.data == 'delete_operation':
        id_ = message.message.text.split("`")[1].lower()
        if db.del_operation(id_):
            bot.answer_callback_query(message.id,
                                      text='Операция удалена!',
                                      cache_time=1)
            operation = db.get_operation(id_)
            msg = msg_operation_list_bad(operation)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_operation_active())
        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'active_operation':
        id_ = message.message.text.split("`")[1].lower()
        if db.recovery_operation(id_):
            operation = db.get_operation(id_, is_active=True)
            msg = msg_operation_list(operation)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_operation(1))
            bot.answer_callback_query(message.id,
                                      text='Операция восстановлена!',
                                      cache_time=1)

        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'yet_operation':
        i = 5
        id_ = message.message.text.split("`")[1].lower()
        product = message.message.text.split('`')[5].lower()
        try:
            yet = db.get_operation(id_, is_active=True)['id']
        except IndexError:
            yet = db.get_operation(id_)['id']
            bot.answer_callback_query(
                message.id,
                '🤖Я не знаю кто следующий, потому что эта операция '
                'удалена...\n🤪Лайфхак: Удали и сразу '
                'восстанови предыдущую запись!')
        bot.edit_message_reply_markup(message.message.chat.id,
                                      message.message.message_id,
                                      reply_markup=key_inline_operation(0))
        operation_list = db.get_operations_yet(product=product, limit=i,
                                               yet=yet, next=False)

        operation_list_id = []
        for operation in operation_list:
            operation_list_id.append(operation['id'])
        if len(operation_list_id) == 5:
            i = 10
        if len(operation_list_id) == 0:
            bot.answer_callback_query(message.id, 'Это последняя операция '
                                                  'в списке')
        if len(operation_list_id) >= 5:
            operation_list_id = operation_list_id[:5]
        for operation in db.get_operations_yet(
                product=product, list_id=operation_list_id, next=True, yet=yet,
                limit=i):
            msg = msg_operation_list(operation)
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id, msg,
                             reply_markup=key_inline_operation(i))
            i -= 1

    if message.data == 'edit_instruction':
        bot.clear_step_handler_by_chat_id(message.message.chat.id)
        old_instruction_dict = {}
        old_url = \
            message.message.json['reply_markup']['inline_keyboard'][0][0][
                'url']
        old_instruction_name = \
            message.message.json['reply_markup']['inline_keyboard'][0][0][
                'text'].split('👀')[1].lower()
        old_instruction_dict['instruction_name'] = old_instruction_name
        old_instruction_dict['url'] = old_url
        bot.answer_callback_query(message.id)
        send = bot.send_message(message.message.chat.id,
                                'Введите название инструкции👇',
                                reply_markup=key_admin_close(
                                    old_instruction_dict['instruction_name'],
                                    old_instruction_dict['instruction_name']))
        bot.register_next_step_handler(
            send, add_instruction, edit=True,
            old_instruction_dict=old_instruction_dict)
    if message.data == 'delete_instruction':
        url = \
            message.message.json['reply_markup']['inline_keyboard'][0][0][
                'url']
        if db.del_instruction(url):
            bot.answer_callback_query(message.id,
                                      text='Инструкция удалена!',
                                      cache_time=1)
            instruction = db.get_instruction(url)
            msg = msg_instruction_list_bad(instruction)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_instruction_active(
                                      instruction))
        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'active_instruction':
        url = \
            message.message.json['reply_markup']['inline_keyboard'][0][0][
                'url']
        if db.recovery_instruction(url):
            instruction = db.get_instruction(url, is_active=True)
            msg = msg_instruction_list(instruction)
            bot.edit_message_text(message_id=message.message.message_id,
                                  chat_id=message.message.chat.id,
                                  text=msg,
                                  reply_markup=key_inline_instruction(
                                      instruction, 1))
            bot.answer_callback_query(message.id,
                                      text='Инструкция восстановлена!',
                                      cache_time=1)

        else:
            bot.answer_callback_query(message.id,
                                      text='Что-то пошло не так!',
                                      cache_time=1)
    if message.data == 'yet_instruction':
        i = 5
        url = \
            message.message.json['reply_markup']['inline_keyboard'][0][0][
                'url']
        try:
            yet = db.get_instruction(url, is_active=True)
        except IndexError:
            yet = db.get_instruction(url)
            bot.answer_callback_query(
                message.id,
                '🤖Я не знаю кто следующий, потому что эта инструкция '
                'удалена...\n🤪Лайфхак: Удали и сразу '
                'восстанови предыдущую запись!')
        bot.edit_message_reply_markup(
            message.message.chat.id,
            message.message.message_id,
            reply_markup=key_inline_instruction(yet, 0))
        instruction_list = db.get_instructions(i, yet=yet['id'], next=False)
        instruction_list_id = []
        for instruction in instruction_list:
            instruction_list_id.append(instruction['id'])
        if len(instruction_list_id) == 0:
            i = 10
            bot.answer_callback_query(message.id, 'Это последняя инструкция в '
                                                  'списке')
        if len(instruction_list_id) >= 5:
            instruction_list_id = instruction_list_id[:5]
        for instruction in db.get_instructions(list_id=instruction_list_id,
                                               next=True, limit=5,
                                               yet=yet['id']):
            msg = msg_instruction_list(instruction)
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id, msg,
                             reply_markup=key_inline_instruction(instruction,
                                                                 i))
            i -= 1

    if message.data == 'yet_instruction_emp':
        i = 5
        url = \
            message.message.json['reply_markup']['inline_keyboard'][0][0][
                'url']
        try:
            yet = db.get_instruction(url, is_active=True)
        except IndexError:
            yet = db.get_instruction(url)
            bot.answer_callback_query(
                message.id,
                '🤖Я не знаю кто следующий, потому что эта инструкция '
                'удалена...\n🤪Лайфхак: Удали и сразу '
                'восстанови предыдущую запись!')
        bot.edit_message_reply_markup(message.message.chat.id,
                                      message.message.message_id,
                                      reply_markup=key_inline_instruction_employee(
                                          instruction=yet))
        instruction_list = db.get_instructions(i, yet=yet['id'], next=False)
        instruction_list_id = []
        for instruction in instruction_list:
            instruction_list_id.append(instruction['id'])
        if len(instruction_list_id) == 0:
            i = 10
            bot.answer_callback_query(message.id, 'Это последняя инструкция в '
                                                  'списке')
        if len(instruction_list_id) >= 5:
            instruction_list_id = instruction_list_id[:5]
        for instruction in db.get_instructions(list_id=instruction_list_id,
                                               next=True, limit=5,
                                               yet=yet['id']):
            msg = msg_instruction_list(instruction)
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id, msg,
                             reply_markup=key_inline_instruction_employee(
                                 instruction, i))
            i -= 1

    if message.data == 'this_month':
        date_now = datetime.now()
        month = date_now.month
        year = date_now.year
        salary = db.get_salary(message.from_user.id, year, month)
        msg = f"🥇 В этом месяце вы заработали:\n💷 {salary} руб."
        bot.answer_callback_query(message.id)
        bot.edit_message_text(message_id=message.message.message_id,
                              chat_id=message.message.chat.id,
                              text=msg,
                              reply_markup=key_inline_salary(message.data))
    if message.data == 'last_month':
        date_now = datetime.now()
        month = date_now.month - 1
        year = date_now.year
        if month == 0:
            year -= 1
            month = 12
        salary = db.get_salary(message.from_user.id, year, month)
        msg = f"🥇 В прошлом месяце вы заработали:\n💷 {salary} руб."
        bot.answer_callback_query(message.id)
        bot.edit_message_text(message_id=message.message.message_id,
                              chat_id=message.message.chat.id,
                              text=msg,
                              reply_markup=key_inline_salary(message.data))
    if message.data == 'salary_today':
        date_now = datetime.now()
        month = date_now.month
        year = date_now.year
        day = date_now.day
        salary = db.get_salary(message.from_user.id, year, month, day=day)
        msg = f"🥇 Сегодня вы заработали:\n💷 {salary} руб."
        bot.answer_callback_query(message.id)
        bot.edit_message_text(message_id=message.message.message_id,
                              chat_id=message.message.chat.id,
                              text=msg,
                              reply_markup=key_inline_salary(message.data))
    if message.data == 'salary_yesterday':
        date_now = datetime.now()
        date_yesterday = date_now - timedelta(days=1)
        month = date_yesterday.month
        year = date_yesterday.year
        day = date_yesterday.day
        salary = db.get_salary(message.from_user.id, year, month, day=day)
        msg = f"🥇 Вчера вы заработали:\n💷 {salary} руб."
        bot.answer_callback_query(message.id)
        bot.edit_message_text(message_id=message.message.message_id,
                              chat_id=message.message.chat.id,
                              text=msg,
                              reply_markup=key_inline_salary(message.data))

    if message.data == 'report_this_month':
        date_now = datetime.now()
        month = date_now.month
        year = date_now.year
        data_dict = {
            'Продукт': [], 'Операция': [], 'Цех': [], 'Цена': [],
            'Количество': []
        }
        month = name_month_str()[month]
        data_user_and_salary = [['Сотрудник'],
                                ['Должность'],
                                ['Тел:'],
                                [f'Зарплата за {month} {year} г.']]
        users = db.get_profiles(limit=orig_limit)
        if users:
            data_list_read = []
            data_sheet_name = []
            for user in users:
                month = name_month_int()[month]
                data = db.get_work_data(user['user_id'], month, year)
                last_first_name = \
                    f"{user['first_name'].title()} {user['last_name'].title()}"
                data_user_and_salary[0].append(last_first_name)
                for report in data:
                    data_dict['Продукт'].append(report['w_product'])
                    data_dict['Операция'].append(report['w_operation'])
                    data_dict['Цех'].append(report['w_workshop'])
                    data_dict['Цена'].append(report['w_price'])
                    data_dict['Количество'].append(report['w_quantity'])
                user_salary = 0
                i = len(data_dict['Цена'])
                while i > 0:
                    user_salary += data_dict['Цена'][i - 1] * \
                                   data_dict['Количество'][i - 1]
                    i -= 1
                data_user_and_salary[3].append(user_salary)
                data_user_and_salary[1].append(user['position'])
                data_user_and_salary[2].append(user['number'])
                month = name_month_str()[month]
                file = f"{last_first_name} - {month} {year} - {user['user_id']}"
                to_excel(data_dict, data_user_and_salary, file)
                data_dict = {
                    'Продукт': [], 'Операция': [], 'Цех': [], 'Цена': [],
                    'Количество': [],
                }
                data_user_and_salary = [['Сотрудник'],
                                        ['Должность'],
                                        ['Тел:'],
                                        [f'Зарплата за {month} {year} г.']]
                read_file = pandas.read_excel(f'reports/{file}.xlsx')
                data_list_read.append(read_file)
                data_sheet_name.append(''.join(last_first_name.split(' ')))
            try:
                one_file_excel(f'{month} {year}', data_sheet_name,
                               data_list_read)
                shutil.make_archive(
                    f'report_zip/Отчеты-{month}-{year}', 'zip', 'reports')
                bot.answer_callback_query(message.id)
                bot.send_document(
                    message.message.chat.id,
                    open(f'report_zip/Отчеты-{month}-{year}.zip', 'rb', ))
                bot.send_message(message.message.chat.id,
                                 f'👆Отчеты за {month.lower()} {year} г. 👆',
                                 reply_markup=key_admin())
                file_list = [f for f in os.listdir('reports') if
                             f.endswith(".xlsx")]
            except (FileNotFoundError, PermissionError):
                bot.send_message(message.message.chat.id,
                                 '😤Не издевайся надо мной...')
            for f in file_list:
                os.remove(os.path.join('reports', f))
            file_list = [f for f in os.listdir('report_zip') if
                         f.endswith(".zip")]
            for f in file_list:
                os.remove(os.path.join('report_zip', f))
        else:
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id,
                             '🤷В базе еще нет сотрудников',
                             reply_markup=key_admin())
    if message.data == 'report_last_month':
        date_now = datetime.now()
        month = date_now.month - 1
        year = date_now.year
        if month == 0:
            month = 12
            year -= 1
        data_dict = {
            'Продукт': [], 'Операция': [], 'Цех': [], 'Цена': [],
            'Количество': []
        }
        month = name_month_str()[month]
        data_user_and_salary = [['Сотрудник'],
                                ['Должность'],
                                ['Тел:'],
                                [f'Зарплата за {month} {year} г.']]
        users = db.get_profiles(limit=orig_limit)
        if users:
            data_list_read = []
            data_sheet_name = []
            for user in users:
                month = name_month_int()[month]
                data = db.get_work_data(user['user_id'], month, year)
                last_first_name = \
                    f"{user['first_name'].title()} {user['last_name'].title()}"
                data_user_and_salary[0].append(last_first_name)
                for report in data:
                    data_dict['Продукт'].append(report['w_product'])
                    data_dict['Операция'].append(report['w_operation'])
                    data_dict['Цех'].append(report['w_workshop'])
                    data_dict['Цена'].append(report['w_price'])
                    data_dict['Количество'].append(report['w_quantity'])
                user_salary = 0
                i = len(data_dict['Цена'])
                while i > 0:
                    user_salary += data_dict['Цена'][i - 1] * \
                                   data_dict['Количество'][i - 1]
                    i -= 1
                data_user_and_salary[3].append(user_salary)
                data_user_and_salary[1].append(user['position'])
                data_user_and_salary[2].append(user['number'])
                month = name_month_str()[month]
                file = f"{last_first_name} - {month} {year} - {user['user_id']}"
                to_excel(data_dict, data_user_and_salary, file)
                data_dict = {
                    'Продукт': [], 'Операция': [], 'Цех': [], 'Цена': [],
                    'Количество': []
                }
                data_user_and_salary = [['Сотрудник'],
                                        ['Должность'],
                                        ['Тел:'],
                                        [f'Зарплата за {month} {year} г.']]
                read_file = pandas.read_excel(f'reports/{file}.xlsx')
                data_list_read.append(read_file)
                data_sheet_name.append(''.join(last_first_name.split(' ')))
            try:
                one_file_excel(f'{month} {year}', data_sheet_name,
                               data_list_read)
                shutil.make_archive(
                    f'report_zip/Отчеты-{month}-{year}', 'zip', 'reports')
                bot.answer_callback_query(message.id)
                bot.send_document(
                    message.message.chat.id,
                    open(f'report_zip/Отчеты-{month}-{year}.zip', 'rb', ))
                bot.send_message(message.message.chat.id,
                                 f'👆Отчеты за {month.lower()} {year} г. 👆',
                                 reply_markup=key_admin())
                file_list = [f for f in os.listdir('reports') if
                             f.endswith(".xlsx")]
                for f in file_list:
                    os.remove(os.path.join('reports', f))
                file_list = [f for f in os.listdir('report_zip') if
                             f.endswith(".zip")]
                for f in file_list:
                    os.remove(os.path.join('report_zip', f))
            except (FileNotFoundError, PermissionError):
                bot.send_message(message.message.chat.id,
                                 '😤Не издевайся надо мной...')
        else:
            bot.answer_callback_query(message.id)
            bot.send_message(message.message.chat.id,
                             '🤷В базе еще нет сотрудников',
                             reply_markup=key_admin())
    if message.data == 'report_month_year':
        bot.answer_callback_query(message.id)
        send = bot.send_message(message.message.chat.id,
                                '👇Введите месяц и год в формате "ММ.ГГГГ"👇',
                                reply_markup=key_close())
        bot.register_next_step_handler(send, main_report)


# t = threading.Thread(target=run_bot)
# t.start()

bot.polling(none_stop=True)
