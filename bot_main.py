import telebot
from telebot import types

# Токен, который вы получили от BotFather
TOKEN = 'Тут ваш токен'

# Создаём экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения последнего текста пользователя и его выбора
user_data = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f'Привет, {message.from_user.first_name}!\nВведи текст:')

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Введите текст любого содержания, в котором есть габариты, например\n'
                                      '<b>привет, планируется отправка с Санкт-Петербурга в Москву '
                                      'паллет 1.2х0.8х1, коробка 0.5х0.4х0.5, ящик 3х3х3</b>\n\nДалее'
                                      ' выбери единицу измерения, в которой представлены габариты в тексте', parse_mode='html')

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    user_text = message.text

    # Сохранение текста в словаре user_data
    user_data[user_id] = {'text': user_text}

    # Создание inline-клавиатуры с кнопками
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Миллиметры', callback_data='mm')
    button2 = types.InlineKeyboardButton('Сантиметры', callback_data='sm')
    button3 = types.InlineKeyboardButton('Метры', callback_data='m')
    keyboard.row(button1, button2, button3)

    # Отправляем сообщение с кнопками
    bot.reply_to(message, 'Выбери единицу измерения габаритов в тексте', reply_markup=keyboard)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.message.chat.id
    if user_id not in user_data:
        bot.answer_callback_query(call.id, "Ошибка: текст не найден.")
        return

    # Получаем последний текст пользователя
    user_text = user_data[user_id]['text']

    if call.data == 'mm':
        ke = 'мм'
    elif call.data == 'sm':
        ke = 'см'
    elif call.data == 'm':
        ke = 'м'


    text = user_text.split()

    chars = ['*', 'x', 'х', '+', 'на']

    packages = []

    def transformation_text(text):
        itog = {}
        for i in text:
            for j in i.split():
                for k in chars:
                    if j.count(k) == 2:
                        nonlocal packages
                        packages.append(j)
                        itog.setdefault(k, []).append(j)
        return itog

    units = {'м': lambda x: x,
             'см': lambda x: x / 100,
             'мм': lambda x: x / 1000}

    def calculation(itog, units, packages):
        from math import prod
        for key, value in itog.items():
            itog[key] = sum(list(map(lambda x: prod([units[ke](int(i)) for i in x.split(key)]), value)))
        cha = '\n'
        return (f'ваши габариты:\n{cha.join(packages)}\nОбщее количество мест: {len(packages)}\nИтоговый объём мест: '
                f'{sum(itog.values())}')
    bot.send_message(user_id, calculation(transformation_text(text), units, packages))

    # Запоминаем последний выбор пользователя
    user_data[user_id]['choice'] = call.data

    # Подтверждаем нажатие кнопки
    bot.answer_callback_query(call.id, "Действие выполнено.")

# Запуск бота
if __name__ == '__main__':
    bot.infinity_polling()