import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import json
import os
from admin import handle_admin_view, handle_cancel_booking  # Импорт функций из admin.py

bot = telebot.TeleBot('8049113028:AAGOtbAF0wp1-jITP17sD_lgNVNj59DmyhU')

# ID адміністратора або групи
ADMIN_CHAT_ID = '7509368619'

user_states = {}
booked_dates = {}
BOOKED_DATES_FILE = 'booked_dates.json'

def load_booked_dates():
    if os.path.exists(BOOKED_DATES_FILE):
        with open(BOOKED_DATES_FILE, 'r') as file:
            try:
                dates = json.load(file)
                return dates
            except json.JSONDecodeError:
                return {}
    return {}

def save_booked_dates():
    with open(BOOKED_DATES_FILE, 'w') as file:
        json.dump(booked_dates, file, indent=4)

booked_dates = load_booked_dates()

def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("📅 Бронювання")
    btn2 = KeyboardButton("🍸 Меню")
    btn3 = KeyboardButton("🌐 Соц мережі")
    btn4 = KeyboardButton("📞 Адміністратор")
    btn5 = KeyboardButton("⚠️ Правила")
    btn_main_menu = KeyboardButton("⭐ Головне меню")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn_main_menu)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = create_main_menu()
    photo_url = 'https://bartrigger.com.ua/content/uploads/images/fresh-cocktails-with-ice-lemon-lime-fruits-generative-ai.jpg'
    welcome_text = """
🍸 Привіт! Ласкаво просимо до Vilnyi – місця, де кожен ковток наповнений свободою! 🍹

Ми раді вітати тебе в нашому барі. Тут ти знайдеш широкий асортимент напоїв для будь-якого настрою. Обирай, замовляй та насолоджуйся смаком!

Через меню ти можеш забронювати стіл та ознайомитися з правилами нашого закладу. Гарного відпочинку!

З повагою, команда «Bar Vilnyi»
    """
    bot.send_photo(message.chat.id, photo=photo_url, caption=welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🍸 Меню")
def ask_to_open_menu(message):
    menu_url = "https://gastrobar-vilnii.ps.me"
    markup = InlineKeyboardMarkup()
    open_button = InlineKeyboardButton("Відкрити в браузері", url=menu_url)
    markup.add(open_button)
    bot.reply_to(message, "Бажаєте відкрити меню в браузері?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🌐 Соц мережі")
def ask_to_open_social_networks(message):
    markup = InlineKeyboardMarkup()
    instagram_button = InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/barvilnyi?igsh=NGNmODBkNDhtЗDFo")
    markup.add(instagram_button)
    bot.reply_to(message, "Оберіть соцмережу:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📞 Адміністратор")
def ask_to_call_admin(message):
    bot.reply_to(message, "Контактний номер адміністратора: +380963332020")

@bot.message_handler(func=lambda message: message.text == "⚠️ Правила")
def show_rules(message):
    rules_text = """
    Правила:
    1. Бронювання столиків у «Vilnyi bar» здійснюється через цей чат-бот 
і не дає права вільного проходження, так як представники «Vilnyi Bar» можуть відмовити у відвідуванні особам, які:
- перебувають у стані надмірного алкогольного сп'яніння чи наркотичного сп'яніння.
- ведуть себе агресивно та образливо по відношенню до представників бару і гостей.
- Не розділяють наших поглядів стосовно відсутності шотів на барі і суши в меню  

    2. Забронювати стіл у п'ятницю та суботу можна на 2 години максимум для однієї компанії, далі гості можуть розміститися біля барної стійки. 
    Бронювання столів на різні часові інтервали заборонено. ( Якщо ви бажаєте забронювати стіл більше ніж на 2 години- звʼяжіться з адміністрацією)

    3. Резерв зберігається протягом 15 хвилин після затвердженого часу після закінчення 15 хв. він автоматично анулюється. 

    4. Бронювання місць за баром не передбачено.
Представники « Vilnyi Bar» можуть відмовити у відвідуванні, зважаючи на переповнений бар – що згодом може призвести до некомфортного перебування всіх гостей.

    5. Компанія більше 4 осіб не може зайняти місця за баром, навіть за наявності вільних місць.

    6. Формат одягу: вільний

    7.  У «Bar Vilnyi» заборонено:
- палити 
- перебувати в зоні сервіс-бару та проходах, заважаючи пересуватися команді бару.
- чіпати руками барний інвентар без дозволу бармена;
- представники бару мають право відмовити гостю у подальшому продажу алкогольної продукції у разі його перебування «на межі сп'яніння» з метою безпеки самого гостя.
У разі порушення правил та положень представники бару будуть змушені розрахувати гостей і останні негайно залишають "Bar Vilnyi".

    З повагою, команда «Bar Vilnyi»

    """
    bot.reply_to(message, rules_text)

@bot.message_handler(func=lambda message: message.text == "📅 Бронювання")
#def ask_for_date(message):
    available_dates = get_next_dates(5)
    date_buttons = ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(0, len(available_dates), 2):
        row = []
        for j in range(2):
            if i + j < len(available_dates):
                row.append(KeyboardButton(available_dates[i + j].strftime("%d-%m-%Y")))
        date_buttons.add(*row)

    date_buttons.add(KeyboardButton("⭐ Головне меню"))
    
    user_states[message.from_user.id] = {'step': 'waiting_for_date'}
    bot.reply_to(message, "Оберіть дату для бронювання:", reply_markup=date_buttons)

def get_next_dates(num_days):
    today = datetime.date.today()
    return [today + datetime.timedelta(days=i) for i in range(num_days)]

@bot.message_handler(func=lambda message: message.text == "⭐ Головне меню")
def handle_main_menu_button(message):
    markup = create_main_menu()
    bot.send_message(message.chat.id, "Повертаємося до головного меню", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in [date.strftime("%d-%m-%Y") for date in get_next_dates(5)], content_types=['text'])
def handle_date_selection(message):
    if message.text == "⭐ Головне меню":
        handle_main_menu_button(message)
        return
    
    user_id = message.from_user.id
    selected_date = message.text

    user_states[user_id]['selected_date'] = selected_date
    user_states[user_id]['step'] = 'waiting_for_table_selection'
    
    table_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    table_buttons.add(KeyboardButton("1 стіл (6 місць)"), KeyboardButton("2 стіл (2 місця)"))
    table_buttons.add(KeyboardButton("3 стіл (4 місця)"), KeyboardButton("4 стіл (2 місця)"))
    table_buttons.add(KeyboardButton("5 стіл (6 місць)"), KeyboardButton("6 стіл (4 місця)"))
    table_buttons.add(KeyboardButton("⭐ Головне меню"))

    bot.reply_to(message, "Оберіть стіл:", reply_markup=table_buttons)

@bot.message_handler(func=lambda message: message.text in ["1 стіл (6 місць)", "2 стіл (2 місця)", "3 стіл (4 місця)", "4 стіл (2 місця)", "5 стіл (6 місць)", "6 стіл (4 місця)"])
def handle_table_selection(message):
    if message.text == "⭐ Головне меню":
        handle_main_menu_button(message)
        return
    
    user_id = message.from_user.id
    selected_table = message.text

    user_states[user_id]['selected_table'] = selected_table
    user_states[user_id]['step'] = 'waiting_for_time'
    
    time_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    time_buttons.add(KeyboardButton("ОБІД"), KeyboardButton("ВЕЧІР"))
    time_buttons.add(KeyboardButton("⭐ Головне меню"))

    bot.reply_to(message, "Оберіть час (ОБІД, ВЕЧІР):", reply_markup=time_buttons)

@bot.message_handler(func=lambda message: message.text in ["ОБІД", "ВЕЧІР"])
def handle_time_selection(message):
    if message.text == "⭐ Головне меню":
        handle_main_menu_button(message)
        return

    user_id = message.from_user.id
    selected_time = message.text
    user_states[user_id]['selected_time'] = selected_time
    user_states[user_id]['step'] = 'waiting_for_final_time'

    if selected_time == "ОБІД":
        available_times = get_available_times(12, 16, user_states[user_id]['selected_date'], user_states[user_id]['selected_table'])
    else:  
        available_times = get_available_times(16, 21, user_states[user_id]['selected_date'], user_states[user_id]['selected_table'])

    time_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    for time in available_times:
        time_buttons.add(KeyboardButton(time.strftime("%H:%M")))

    time_buttons.add(KeyboardButton("Назад"), KeyboardButton("⭐ Головне меню"))

    bot.reply_to(message, "Оберіть точний час:", reply_markup=time_buttons)

def get_available_times(start_hour, end_hour, selected_date, selected_table):
    times = []
    for hour in range(start_hour, end_hour):
        for minute in [0]:
            time = datetime.time(hour)
            time_to_check = datetime.datetime.combine(datetime.date.today(), time)
            if check_if_time_available(selected_date, time_to_check.strftime("%H:%M"), selected_table):
                times.append(time_to_check)
    return times

def check_if_time_available(selected_date, selected_time, selected_table):
    global booked_dates
    booked_dates = load_booked_dates()  # Обновляем данные из файла при каждом вызове функции

    for key in booked_dates:
        if selected_date in key and selected_time in key and selected_table in key:
            return False
    return True


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('step') == 'waiting_for_final_time')
def handle_final_time_selection(message):
    user_id = message.from_user.id

    if message.text == "⭐ Головне меню":
        handle_main_menu_button(message)
        return

    if message.text == "Назад":
        user_states[user_id]['step'] = 'waiting_for_time'
        time_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        time_buttons.add(KeyboardButton("ОБІД"), KeyboardButton("ВЕЧІР"))
        time_buttons.add(KeyboardButton("⭐ Головне меню"))
        bot.reply_to(message, "Оберіть час (ОБІД, ВЕЧІР):", reply_markup=time_buttons)
        return

    selected_time = message.text
    user_states[user_id]['final_time'] = selected_time
    user_states[user_id]['step'] = 'waiting_for_period'

    period_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    period_buttons.add(KeyboardButton("1 година"), KeyboardButton("2 години"))
    period_buttons.add(KeyboardButton("⭐ Головне меню"))

    bot.reply_to(message, "На який період потрібен столик? 1 година чи 2 години?", reply_markup=period_buttons)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('step') == 'waiting_for_period')
def handle_period_selection(message):
    if message.text == "⭐ Головне меню":
        handle_main_menu_button(message)
        return

    user_id = message.from_user.id
    selected_period = message.text

    if selected_period not in ["1 година", "2 години"]:
        bot.reply_to(message, "Будь ласка, оберіть 1 або 2 години.")
        return

    user_states[user_id]['selected_period'] = selected_period
    user_states[user_id]['step'] = 'waiting_for_name'

    bot.reply_to(message, "Будь ласка, введіть ваше ім'я:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('step') == 'waiting_for_name')
def handle_name_input(message):
    if message.text == "⭐ Головне меню":
        handle_main_menu_button(message)
        return

    user_id = message.from_user.id
    user_name = message.text
    user_states[user_id]['name'] = user_name

    contact_button = ReplyKeyboardMarkup(resize_keyboard=True)
    contact_button.add(KeyboardButton("Поділитися номером", request_contact=True))
    contact_button.add(KeyboardButton("⭐ Головне меню"))

    user_states[user_id]['step'] = 'waiting_for_contact'
    bot.reply_to(message, "Будь ласка, поділіться своїм номером телефону:", reply_markup=contact_button)

@bot.message_handler(content_types=['contact'])
def handle_contact_input(message):
    user_id = message.from_user.id
    if user_states.get(user_id, {}).get('step') == 'waiting_for_contact':
        contact = message.contact.phone_number
        user_states[user_id]['phone'] = contact

        selected_date = user_states[user_id]['selected_date']
        final_time = user_states[user_id]['final_time']
        selected_period = user_states[user_id]['selected_period']
        selected_table = user_states[user_id]['selected_table']
        user_name = user_states[user_id]['name']

        booking_datetime = datetime.datetime.strptime(f"{selected_date} {final_time}", "%d-%m-%Y %H:%M")

        block_times(selected_date, final_time, selected_period, selected_table, user_name, contact)

        send_booking_to_admin(booking_datetime, user_name, selected_period, contact, selected_table)

        bot.reply_to(message, f"Ваше бронювання на {booking_datetime.strftime('%d-%m-%Y %H:%M')} підтверджено на {selected_period}. Ми зв'яжемося з вами за номером: {contact}")

def block_times(selected_date, selected_time, selected_period, selected_table, name, phone):
    booking_datetime = datetime.datetime.strptime(f"{selected_date} {selected_time}", "%d-%m-%Y %H:%M")

    period_hours = 1 if selected_period == "1 година" else 2

    for hour in range(period_hours):
        time_to_block = booking_datetime + datetime.timedelta(hours=hour)
        booked_dates[f"{selected_table}_{time_to_block.strftime('%d-%m-%Y %H:%M')}"] = {
            "name": name,
            "phone": phone
        }

    save_booked_dates()

def send_booking_to_admin(booking_datetime, user_name, period, phone, table):
    bot.send_message(ADMIN_CHAT_ID, f"Нове бронювання!\nІм'я: {user_name}\nДата і час: {booking_datetime.strftime('%d-%m-%Y %H:%M')}\nПеріод: {period}\nТелефон: {phone}\nСтіл: {table}")

# Обработка команды /admin_view
@bot.message_handler(commands=['admin_view'])
def admin_view(message):
    handle_admin_view(message, bot)  # Вызов функции из admin.py

# Обработка команды /cancel_booking
@bot.message_handler(commands=['cancel_booking'])
def cancel_booking(message):
    handle_cancel_booking(message, bot)  # Вызов функции для отмены бронирования из admin.py

bot.polling()
