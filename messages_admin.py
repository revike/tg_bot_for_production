def msg_employee_list(profile):
    """Message employee list"""
    return f"๐ `{profile['user_id']}`\n" \
           f"๐ค {profile['first_name'].title()} " \
           f"{profile['last_name'].title()}\n" \
           f"๐  {profile['position'].title()}"


def msg_employee_bad(user):
    """Message employee list (fired)"""
    return f"๐ `{user['user_id']}`\n" \
           f"๐ค {user['first_name'].title()} " \
           f"{user['last_name'].title()}\n" \
           f"๐  {user['position'].title()}\n" \
           f"โ๏ธะกัะฐััั: ะฃะะะะะ!"


def msg_workshop_list(workshop):
    """Message workshop list"""
    return f"๐ช `{workshop['name'].capitalize()}` \n" \
           f"๐ {workshop['description'].capitalize()}"


def msg_workshop_list_bad(workshop):
    """Message workshop list (delete)"""
    return f"๐ช `{workshop['name'].capitalize()}` \n" \
           f"๐ {workshop['description'].capitalize()}\n" \
           f"โ๏ธะกัะฐััั: ะฃะะะะะ!"


def msg_product_list(product):
    """Message product list"""
    return f"๐  `{product['product_name'].capitalize()}` \n"


def msg_product_list_bad(product):
    """Message product list (delete)"""
    return f"๐  `{product['product_name'].capitalize()}` \n" \
           f"โ๏ธะกัะฐััั: ะฃะะะะะ!"


def msg_operation_list(operation):
    """Message operation list"""
    return f"๐ ID - `{operation['id']}` \n" \
           f"๐ฅ ะะฟะตัะฐัะธั: `{operation['operation_name'].capitalize()}` \n" \
           f"๐ข ะฆะตั: {operation['name'].capitalize()} \n" \
           f"๐  ะัะพะดัะบั: {operation['product_name'].capitalize()} \n" \
           f"๐ต ะกัะพะธะผะพััั: {operation['price']} ััะฑ."


def msg_operation_list_bad(operation):
    """Message operation list (delete)"""
    return f"๐ ID - `{operation['id']}` \n" \
           f"๐ฅ ะะฟะตัะฐัะธั: `{operation['operation_name'].capitalize()}` \n" \
           f"๐ข ะฆะตั: {operation['name'].capitalize()} \n" \
           f"๐  ะัะพะดัะบั: {operation['product_name'].capitalize()} \n" \
           f"๐ต ะกัะพะธะผะพััั: {operation['price']} ััะฑ. \n" \
           f"โ๏ธะกัะฐััั: ะฃะะะะะ!"


def msg_save_operation(operation_data):
    """Message for save operation"""
    return f"๐ฅ ะะฟะตัะฐัะธั: `{operation_data['operation_name'].capitalize()}`\n" \
           f"๐ข ะฆะตั: {operation_data['name'].capitalize()}\n" \
           f"๐  ะัะพะดัะบั: {operation_data['product_name'].capitalize()}\n" \
           f"๐ต ะกัะพะธะผะพััั: {operation_data['price']} ััะฑ.\n" \
           f"โะกะพััะฐะฝะธัั?"


def msg_instruction_list(instruction):
    """Message for save instruction"""
    return f"๐ `{instruction['instruction_name'].capitalize()}`"


def msg_instruction_list_bad(instruction):
    """Message for save instruction (delete)"""
    return f"๐ `{instruction['instruction_name'].capitalize()}`\n" \
           f"โ๏ธะกัะฐััั: ะฃะะะะะะ!"
