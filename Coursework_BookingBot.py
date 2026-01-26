import telebot 
from telebot import types
import sqlite3

bot = telebot.TeleBot('Ваш токен')

# Функция создает таблицу, демонстрационный вариант
def init_database():
    conn = sqlite3.connect('barbershop.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barbershop (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barber_name VARCHAR(30),
            app_date VARCHAR(15),
            app_time VARCHAR(15)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных инициализирована")

init_database()


# Обработчик команды старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добрый день, добро пожаловать в бот для записи в барбершоп')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = types.KeyboardButton("Запись к специалисту")
    b2 = types.KeyboardButton("Запись к любому специалисту")
    markup.add(b1, b2)
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

# Функция для добавления свободных дат из базы, в inline клавиатуру под сообщением
def send_date_buttons(chat_id):
    markup = types.InlineKeyboardMarkup()
    conn = sqlite3.connect('barbershop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT app_date FROM barbershop ORDER BY app_date')
    dates_result = cursor.fetchall()
    conn.close()
    
    dates = [date[0] for date in dates_result]
    
    for i in range(0, len(dates), 2):
        if i + 1 < len(dates):
            btn1 = types.InlineKeyboardButton(dates[i], callback_data=f'date_{dates[i]}')
            btn2 = types.InlineKeyboardButton(dates[i+1], callback_data=f'date_{dates[i+1]}')
            markup.row(btn1, btn2)
        else:
            btn = types.InlineKeyboardButton(dates[i], callback_data=f'date_{dates[i]}')
            markup.row(btn)
    
    bot.send_message(chat_id, "Выберите удобную дату:", reply_markup=markup)

# Функция для добавления свободного времени, в inline клавиатуру под сообщением
def send_time_buttons(chat_id, selected_date, barber_name):
    markup = types.InlineKeyboardMarkup()
    conn = sqlite3.connect('barbershop.db')
    cursor = conn.cursor() 
    if "Любой специалист" in barber_name:
        cursor.execute('SELECT DISTINCT app_time FROM barbershop WHERE app_date = ? ORDER BY app_time', (selected_date,))
    else:
        cursor.execute('SELECT DISTINCT app_time FROM barbershop WHERE app_date = ? AND barber_name = ? ORDER BY app_time', 
                      (selected_date, barber_name))
        
    times_result = cursor.fetchall()
    conn.close()
    times = [time[0] for time in times_result]
    
    if not times:
        bot.send_message(chat_id, "На выбранную дату нет свободного времени")
        return

    for i in range(0, len(times), 3):
        if i + 2 < len(times):
            btn1 = types.InlineKeyboardButton(times[i], callback_data=f'time_{times[i]}')
            btn2 = types.InlineKeyboardButton(times[i+1], callback_data=f'time_{times[i+1]}')
            btn3 = types.InlineKeyboardButton(times[i+2], callback_data=f'time_{times[i+2]}')
            markup.row(btn1, btn2, btn3)
        elif i + 1 < len(times):
            btn1 = types.InlineKeyboardButton(times[i], callback_data=f'time_{times[i]}')
            btn2 = types.InlineKeyboardButton(times[i+1], callback_data=f'time_{times[i+1]}')
            markup.row(btn1, btn2)
        else:
            btn = types.InlineKeyboardButton(times[i], callback_data=f'time_{times[i]}')
            markup.row(btn)
    
    bot.send_message(chat_id, "Выберите удобное время:", reply_markup=markup)

# Функция для обработки ответов пользователя кнопок
def on_click(message):
    if message.text == "Запись к специалисту" :
         markup = types.InlineKeyboardMarkup()
         btn1 = types.InlineKeyboardButton("Антон", callback_data='specialist_anton')
         btn2 = types.InlineKeyboardButton("Вячеслав", callback_data='specialist_slavik')
         markup.row(btn1, btn2)
         bot.send_message(message.chat.id, "Выберите специалиста", reply_markup=markup)
    elif message.text == "Запись к любому специалисту":
         markup = types.InlineKeyboardMarkup()
         btn3 = types.InlineKeyboardButton("Мужская стрижка", callback_data='man_cut')
         btn4 = types.InlineKeyboardButton("Женская стрижка", callback_data='wman_cut')
         markup.row(btn3, btn4)
         bot.send_message(message.chat.id, "Выберите услугу", reply_markup=markup)

user_data = {}

# Обработчики callback для inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "specialist_anton":
        bot.answer_callback_query(call.id, "Вы выбрали Антона")
        user_data[call.message.chat.id] = {'barber': 'Антон'}
        bot.send_message(call.message.chat.id, "Рабочие дни мастера")
        send_date_buttons(call.message.chat.id)
    elif call.data == "specialist_slavik":
        bot.answer_callback_query(call.id, "Вы выбрали Вячеслава")
        user_data[call.message.chat.id] = {'barber': 'Вячеслав'}
        bot.send_message(call.message.chat.id, "Рабочие дни мастера")
        send_date_buttons(call.message.chat.id)
    elif call.data == "man_cut":
        bot.answer_callback_query(call.id, "Вы выбрали мужскую стрижку")
        user_data[call.message.chat.id] = {'barber': 'Любой специалист (Мужская стрижка)'}
        bot.send_message(call.message.chat.id, "Рабочие дни мастеров")
        send_date_buttons(call.message.chat.id)
    elif call.data == "wman_cut":
        bot.answer_callback_query(call.id, "Вы выбрали женскую стрижку")
        user_data[call.message.chat.id] = {'barber': 'Любой специалист (Женская стрижка)'}
        bot.send_message(call.message.chat.id, "Рабочие дни мастеров")
        send_date_buttons(call.message.chat.id)
    elif call.data.startswith('date_'):
        date = call.data.replace('date_', '')
        bot.answer_callback_query(call.id, f"Вы выбрали дату: {date}")
        if call.message.chat.id in user_data:
            user_data[call.message.chat.id]['date'] = date
            barber_name = user_data[call.message.chat.id].get('barber')
            bot.send_message(call.message.chat.id, "Свободное время в выбранную дату")
            send_time_buttons(call.message.chat.id, date, barber_name)
    elif call.data.startswith('time_'):
        time = call.data.replace('time_', '')
        bot.answer_callback_query(call.id, f"Вы выбрали время: {time}")
        
        if call.message.chat.id in user_data:
            barber_name = user_data[call.message.chat.id].get('barber', 'Неизвестный специалист')
            date = user_data[call.message.chat.id].get('date', 'Неизвестная дата')
            
            conn = sqlite3.connect('barbershop.db')
            cursor = conn.cursor()
            
            if "Любой специалист" in barber_name:
                cursor.execute('DELETE FROM barbershop WHERE app_date = ? AND app_time = ? LIMIT 1', (date, time))
            else:
                cursor.execute('DELETE FROM barbershop WHERE barber_name = ? AND app_date = ? AND app_time = ?', 
                              (barber_name, date, time))
            
            conn.commit()
            conn.close()
            
            bot.send_message(call.message.chat.id, 
                           f"Вы записаны!\n"
                           f"Специалист: {barber_name}\n"
                           f"Дата: {date}\n"
                           f"Время: {time}")
            
            del user_data[call.message.chat.id]


bot.infinity_polling()