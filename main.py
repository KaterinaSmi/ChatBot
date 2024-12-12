from gc import callbacks
from idlelib.rpc import request_queue
from telebot import types
import telebot
import json
import requests
from methods import db_methods

#Bot setUpmport callbacks
from idlelib.rpc import request_queue
from telebot import types
import telebot
import json
import requests
from methods import db_methods

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


def save_new_field_value(message):
    field = edit_context[message.chat.id]["field"]
    person_id = edit_context[message.chat.id]["person_id"]
    new_value = message.text
    #apply the new value to the function in db_methods
    db_methods.update_person_field(db_collection=people_collection, person_id=person_id, person_field=field, new_value=new_value)
    del edit_context[message.chat.id]
    bot.send_message(message.chat.id, f"{field} updated successfully to {new_value}!")


def add_new_field_in_db(message):
    new_field_name = message.text
    edit_context[message.chat.id]["field"] = new_field_name
    bot.send_message(message.chat.id, text=f"You selected '{new_field_name}'. Please provide a value for this field:")
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
            text += f"<b>{key[0].upper()}{key[1:]}</b>: {value}\n"
            if key != "_id":
                button_text = f"Edit {key}"
                callback_data = f'edit_{key}_{person["_id"]}'  # Need a key to search for appropriate data
                row_btns.append(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
            if len(row_btns) == 2:
                markup.row(row_btns[0], row_btns[1])
                row_btns = []
        markup.add(types.InlineKeyboardButton(text="Add new field", callback_data=f'add_new_field_{person["_id"]}'))
        bot.delete_message(callback.message.chat.id, callback.message.id)
        bot.send_message(callback.message.chat.id, text=text, parse_mode='html', reply_markup=markup)

    elif 'edit_' in callback.data:
        our_data = callback.data.split('_')
        field = our_data[1]
        person_id = int(our_data[2])

        #saving the editing context
        edit_context[callback.message.chat.id] = {"field": field, "person_id": person_id}
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Please enter the new value for {field}:"
        )
        bot.register_next_step_handler(callback.message, save_new_field_value)

    elif 'add_new_field_' in callback.data:
        add_new_filed_data = callback.data.split("_")
        person_id = int(add_new_filed_data[3])
        markup = types.ReplyKeyboardMarkup()
        for field in ['city', 'birthday', 'job', 'gender', 'pet', 'hobby', 'department', 'photo']:
            markup.add(types.KeyboardButton(field))
        edit_context[callback.message.chat.id] = {"person_id": person_id}
        bot.send_message(callback.message.chat.id, text="Enter new field name or choose from the following options", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(callback.message, add_new_field_in_db)


#fields for editing:
#city, birthday, job, gender, fullAddress,hobby, pet,  photo, department
if __name__ == '__main__':
    bot.infinity_polling()
