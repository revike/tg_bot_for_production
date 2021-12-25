def msg_employee_list(profile):
    """Message employee list"""
    return f"🆔 `{profile['user_id']}`\n" \
           f"👤 {profile['first_name'].title()} " \
           f"{profile['last_name'].title()}\n" \
           f"🛠 {profile['position'].title()}"


def msg_employee_bad(user):
    """Message employee list (fired)"""
    return f"🆔 `{user['user_id']}`\n" \
           f"👤 {user['first_name'].title()} " \
           f"{user['last_name'].title()}\n" \
           f"🛠 {user['position'].title()}\n" \
           f"✍️Статус: УВОЛЕН!"


def msg_workshop_list(workshop):
    """Message workshop list"""
    return f"🏪 `{workshop['name'].capitalize()}` \n" \
           f"📄 {workshop['description'].capitalize()}"


def msg_workshop_list_bad(workshop):
    """Message workshop list (delete)"""
    return f"🏪 `{workshop['name'].capitalize()}` \n" \
           f"📄 {workshop['description'].capitalize()}\n" \
           f"✍️Статус: УДАЛЕН!"


def msg_product_list(product):
    """Message product list"""
    return f"🎠 `{product['product_name'].capitalize()}` \n"


def msg_product_list_bad(product):
    """Message product list (delete)"""
    return f"🎠 `{product['product_name'].capitalize()}` \n" \
           f"✍️Статус: УДАЛЕН!"


def msg_operation_list(operation):
    """Message operation list"""
    return f"🆔 ID - `{operation['id']}` \n" \
           f"💥 Операция: `{operation['operation_name'].capitalize()}` \n" \
           f"🏢 Цех: {operation['name'].capitalize()} \n" \
           f"🎠 Продукт: `{operation['product_name'].capitalize()}` \n" \
           f"💵 Стоимость: {operation['price']} руб."


def msg_operation_list_bad(operation):
    """Message operation list (delete)"""
    return f"🆔 ID - `{operation['id']}` \n" \
           f"💥 Операция: `{operation['operation_name'].capitalize()}` \n" \
           f"🏢 Цех: {operation['name'].capitalize()} \n" \
           f"🎠 Продукт: {operation['product_name'].capitalize()} \n" \
           f"💵 Стоимость: {operation['price']} руб. \n" \
           f"✍️Статус: УДАЛЕН!"


def msg_save_operation(operation_data):
    """Message for save operation"""
    return f"💥 Операция: `{operation_data['operation_name'].capitalize()}`\n" \
           f"🏢 Цех: {operation_data['name'].capitalize()}\n" \
           f"🎠 Продукт: {operation_data['product_name'].capitalize()}\n" \
           f"💵 Стоимость: {operation_data['price']} руб.\n" \
           f"✅Сохранить?"


def msg_instruction_list(instruction):
    """Message for save instruction"""
    return f"🔘 `{instruction['instruction_name'].capitalize()}`"


def msg_instruction_list_bad(instruction):
    """Message for save instruction (delete)"""
    return f"🔘 `{instruction['instruction_name'].capitalize()}`\n" \
           f"✍️Статус: УДАЛЕНА!"
