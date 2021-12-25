def msg_work_active(get_work, quantity=None):
    """Message for end work"""
    msg = f"🏢Цех: {get_work['w_workshop']}\n" \
          f" 🎠Товар: {get_work['w_product']}\n " \
          f"💥Операция: {get_work['w_operation']}\n " \
          f"💵Цена: {get_work['w_price']} руб/шт.\n "
    if quantity:
        msg += f"🥁Количество: {quantity}\n" \
               f"✅Сохранить?"
    else:
         msg += f"Какое количество сделанного товара? 👇"
    return msg


def msg_work_end():
    """Message work end"""
    return 'После завершения операции\n' \
           'нажмите "🪚Закончить работу",\n' \
           'для ввода количества сделанной продукции и ' \
           'записи данных в зарплатный лист!'


def msg_confirmation(work):
    return f"✅Подтвердите начало выполнения работы\n" \
           f"🏢Цех: {work['workshop']}\n" \
           f"🎠Товар: {work['product']}\n" \
           f"💥Операция: {work['operation']}\n" \
           f"💵Цена: {work['price']}"
