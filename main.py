from gc import callbacks
from idlelib.rpc import request_queue
from telebot import types
import telebot
import json
import requests
from methods import db_methods
from datetime import datetime

#Bot setUpmport callbacks
from idlelib.rpc import request_queue
from telebot import types
import telebot
import json
import requests

from methods import db_methods
from others.consts import HOLIDAYS

#Bot setUp
token = '7765432197:AAHwyBObpdboilKRgNOVF9RVQDtknIdXDVc'
bot = telebot.TeleBot(token)

#context
edit_context = {}

#database configs
db = db_methods.get_database("about_people")
people_collection = db["people"]


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f'Привет, <b>{message.chat.username}</b>',
        parse_mode='html'
    )


@bot.message_handler(commands=['new_person'])
def new_person(message):
    person = db_methods.add_person(db_collection=people_collection)
    bot.send_message(chat_id=message.chat.id, text=f'The user\n\nname = {person["name"]}\nsurname = {person["surname"]}\n\nhas been added')


@bot.message_handler(commands=['all'])
def find_all(message):
    markup = types.InlineKeyboardMarkup()
    all_people = db_methods.get_all(db_collection=people_collection)
    for person in all_people:
        markup.add(types.InlineKeyboardButton(text=f'{person["name"]} {person["surname"]}',callback_data=f'selected_person_{person["_id"]}'))
    bot.send_message(chat_id=message.chat.id, text=f'These people are in database: ', parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['search'])
def search_persons(message):
    if len(message.text.split()) < 2:
        bot.send_message(chat_id=message.chat.id, text="Please provide a name or surname to search.")
        return
    text_message = message.text #get all the text of all the command message
    text_filter = text_message.split(" ")[1]
    #Here is function implementation
    persons = db_methods.search_persons(db_collection=people_collection, text_filter=text_filter)
    markup = types.InlineKeyboardMarkup()
    for person in persons:
        #label!! dynamically adapts to any field we have in dictionary
        markup.add(types.InlineKeyboardButton(text=f'{person["name"]} {person["surname"]}', callback_data=f'selected_person_{person["_id"]}'))
    bot.send_message(chat_id=message.chat.id, text=f'The persons have been found: ', parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['holidays'])
def holidays(message):
    now = datetime.now()
    text = f"Today is {now.day} {now.strftime('%B')}\n\n"
    if now.month in HOLIDAYS and now.day in HOLIDAYS[now.month]["days"]:
        holidays_today = HOLIDAYS[now.month]["days"][now.day]
        text += f'Holidays today:\n<i>{", ".join(holidays_today)}</i>\n\n'
    else:
        text += "No holidays today"
    for month in HOLIDAYS:
        month_name = HOLIDAYS[month]["name"]
        text += f'Holidays in <b>{month_name}</b>:\n'
        for day, holiday_name in HOLIDAYS[month]["days"].items():
            text += f'- <i>{day} of {month_name}</i> is {", ".join(holiday_name)}\n'
        text += "\n"
    bot.send_message(chat_id=message.chat.id, text=text, parse_mode='html')

def save_new_field_value(message):
    # print(json.dumps(message.json, indent=4))
    field = edit_context[message.chat.id]["field"]
    person_id = edit_context[message.chat.id]["person_id"]
    if field == 'photo':
        telegram_file_path = bot.get_file(message.photo[-1].file_id).file_path
        telegram_file = bot.download_file(telegram_file_path)
        file_extension = telegram_file_path.split('.')[-1]
        file_name = f"{person_id}.{file_extension}"
        file_path = f"imgs/people/{file_name}"
        with open(file_path, "wb") as f:
            f.write(telegram_file)
        db_methods.update_person_field(db_collection=people_collection, person_id=person_id, person_field=field, new_value=file_path)
        del edit_context[message.chat.id]
        bot.send_message(message.chat.id, f"Person's photo updated!")
    else:
        new_value = message.text
        #apply the new value to the function in db_methods
        db_methods.update_person_field(db_collection=people_collection, person_id=person_id, person_field=field, new_value=new_value)
        del edit_context[message.chat.id]
        bot.send_message(message.chat.id, f"{field} updated successfully to {new_value}!")


def add_new_field_in_db(message):
    new_field_name = message.text
    edit_context[message.chat.id]["field"] = new_field_name
    bot.send_message(message.chat.id, text=f"You selected '{new_field_name}'. Please provide data for this field:")
    bot.register_next_step_handler(message, save_new_field_value)


@bot.callback_query_handler(func = lambda callback: True)
def callback_message(callback):
    if 'selected_person' in callback.data:
        callback_data_parts = callback.data.split('_')
        person_id = int(callback_data_parts[2])
        person = db_methods.get_person_by_id(db_collection=people_collection, person_id=person_id)
        markup = types.InlineKeyboardMarkup()
        text = 'User\'s data:\n'
        row_btns = []
        for key, value in person.items():
            if key != 'photo':
                text += f"<b>{key[0].upper()}{key[1:]}</b>: {value}\n"
            if key != "_id":
                button_text = f"Edit {key}"
                callback_data = f'edit_{key}_{person["_id"]}'  # Need a key to search for appropriate data
                row_btns.append(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
            if len(row_btns) == 2:
                markup.row(row_btns[0], row_btns[1])
                row_btns = []
        markup.add(types.InlineKeyboardButton(text="Add new field", callback_data=f'add_new_field_{person["_id"]}'))
        markup.add(types.InlineKeyboardButton(text="Delete field", callback_data=f'for_delete_fields_{person["_id"]}'))
        bot.delete_message(callback.message.chat.id, callback.message.id)
        if 'photo' in person:
            bot.send_photo(callback.message.chat.id, photo=open(person["photo"], "rb"), caption=text, parse_mode='html', reply_markup=markup)
        else:
            bot.send_message(callback.message.chat.id, text=text, parse_mode='html', reply_markup=markup)

    elif 'edit_' in callback.data:
        our_data = callback.data.split('_')
        field = our_data[1]
        person_id = int(our_data[2])

        #saving the editing context
        edit_context[callback.message.chat.id] = {"field": field, "person_id": person_id}
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Please enter the new data for {field}:"
        )
        bot.register_next_step_handler(callback.message, save_new_field_value)

    elif 'add_new_field_' in callback.data:
        add_new_filed_data = callback.data.split("_")
        person_id = int(add_new_filed_data[3])
        markup = types.ReplyKeyboardMarkup()
        for field in ['photo', 'city', 'birthday', 'job', 'gender', 'pet', 'hobby', 'department', 'email']:
            markup.add(types.KeyboardButton(field))
        edit_context[callback.message.chat.id] = {"person_id": person_id}
        bot.send_message(callback.message.chat.id, text="Enter new field name or choose from the following options", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(callback.message, add_new_field_in_db)

    elif 'for_delete_fields' in callback.data:
        delete_field_data = callback.data.split("_")
        person_id = int(delete_field_data[-1])
        person = db_methods.get_person_by_id(db_collection=people_collection, person_id=person_id)
        markup = types.InlineKeyboardMarkup()
        row_btns = []
        for key, value in person.items():
            if key not in ["_id", 'surname', 'name']:
                button_text = f"Delete {key}"
                callback_data = f'delete_field_{key}_{person["_id"]}'  # Need a key to search for appropriate data
                row_btns.append(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
            if len(row_btns) == 2:
                markup.row(row_btns[0], row_btns[1])
                row_btns = []
        if len(row_btns) > 0:
            markup.row(row_btns[0])
        bot.send_message(chat_id=callback.message.chat.id, text='Select field to delete:', parse_mode='html', reply_markup=markup)

    elif 'delete_field' in callback.data:
        delete_field_data = callback.data.split("_")
        person_id = int(delete_field_data[-1])
        person_field = delete_field_data[-2]
        db_methods.delete_person_field(db_collection=people_collection, person_id=person_id, person_field=person_field)
        bot.send_message(chat_id=callback.message.chat.id, text=f'The field "{person_field}" was deleted successfully!')

#professions, list of all professional holidays; and birthday format dictionary
#command holidays to handle "/holidays" displays all poss holidays
if __name__ == '__main__':
    bot.infinity_polling()
