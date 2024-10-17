import json
import os
from datetime import datetime

BOOKED_DATES_FILE = 'booked_dates.json'

# Глобальная переменная
booked_dates = {}

def load_booked_dates():
    if os.path.exists(BOOKED_DATES_FILE):
        with open(BOOKED_DATES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_booked_dates(booked_dates):
    with open(BOOKED_DATES_FILE, 'w') as file:
        json.dump(booked_dates, file, indent=4)

def escape_markdown_v2(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars and char != '+' else char for char in text])

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
        return date_obj.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return date_str

def format_phone(phone_str):
    if phone_str.startswith("+38"):
        return phone_str[3:]
    elif phone_str.startswith("38"):
        return phone_str[2:]
    return phone_str

def handle_admin_view(message, bot):
    global booked_dates  # Глобальная переменная для обновления данных
    booked_dates = load_booked_dates()  # Перезагружаем данные при каждом вызове

    if not booked_dates:
        bot.reply_to(message, "Немає жодних бронювань на цей момент.")
        return

    bookings_by_table = {}
    for key, booking in booked_dates.items():
        table, datetime_str = key.split("_", 1)
        if table not in bookings_by_table:
            bookings_by_table[table] = []
        bookings_by_table[table].append({
            "datetime": format_date(datetime_str),
            "name": booking["name"],
            "phone": format_phone(booking["phone"])
        })

    response_text = "📅 Бронювання:\n\n"
    for table, bookings in bookings_by_table.items():
        response_text += f"🔷 <b>Стіл: {table}</b>\n"
        for booking in bookings:
            response_text += (
                f"Дата і час: {booking['datetime']}\n"
                f"Ім'я: {booking['name']}\n"
                f"Телефон: {escape_markdown_v2(booking['phone'])}\n"
                "-----------------------\n"
            )
        response_text += "\n"

    bot.send_message(message.chat.id, response_text, parse_mode="HTML")

# Функция для отмены бронирования
def handle_cancel_booking(message, bot):
    global booked_dates  # Глобальная переменная для обновления данных
    booked_dates = load_booked_dates()  # Перезагружаем данные о бронированиях

    if not booked_dates:
        bot.reply_to(message, "Немає жодних бронювань для скасування.")
        return

    response_text = "🛑 Скасування бронювання:\n\n"
    for idx, (key, booking) in enumerate(booked_dates.items(), 1):
        table, datetime_str = key.split("_", 1)
        response_text += (
            f"{idx}. Стіл: {table}\n"
            f"Дата і час: {datetime_str}\n"
            f"Ім'я: {booking['name']}\n"
            f"Телефон: {booking['phone']}\n"
            "-----------------------\n"
        )

    bot.send_message(message.chat.id, response_text)
    msg = bot.send_message(message.chat.id, "Введіть номер бронювання для скасування:")
    bot.register_next_step_handler(msg, process_cancel_booking, bot)

def process_cancel_booking(message, bot):
    global booked_dates
    try:
        booking_id = int(message.text) - 1
        if booking_id < 0 or booking_id >= len(booked_dates):
            bot.reply_to(message, "Неправильний номер бронювання. Спробуйте ще раз.")
            return

        key_to_remove = list(booked_dates.keys())[booking_id]
        del booked_dates[key_to_remove]
        save_booked_dates(booked_dates)

        # Перезагружаем обновленные данные о бронированиях
        booked_dates = load_booked_dates()

        bot.reply_to(message, "Бронювання успішно скасовано.")
    except ValueError:
        bot.reply_to(message, "Будь ласка, введіть правильний номер.")
    except IndexError:
        bot.reply_to(message, "Номер бронювання не знайдено.")

