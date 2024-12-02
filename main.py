from gc import callbacks
from idlelib.rpc import request_queue
from telebot import types
import telebot
import json
import requests
from methods import db_methods

#Bot setUp
token = '7765432197:AAHwyBObpdboilKRgNOVF9RVQDtknIdXDVc'
bot = telebot.TeleBot(token)

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
        markup.add(types.InlineKeyboardButton(text=f'{person["name"]} {person["surname"]}',callback_data=f'find_all_{person["_id"]}'))
    bot.send_message(chat_id=message.chat.id, text=f'These people are in database: ', parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func = lambda callback: True)
def callback_message_find_all(callback):
    if 'find_all' in callback.data:
        call_back_data = callback.data.split("_")
        person_id = call_back_data[2]

        bot.send_message(callback.message.chat.id, text=text, parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['search'])
def search_persons(message):
    if len(message.text.split()) < 2:
        bot.send_message(chat_id=message.chat.id, text="Please provide a name or surname to search.")
        return
    text_message = message.text #get all the text of all the command message
    text_filter = text_message.split(" ")[1]
    #Here is function implementation
    persons = db_methods.search(db_collection=people_collection, text_filter=text_filter)
    markup = types.InlineKeyboardMarkup()
    for person in persons:
        #label!! dynamically adapts to any field we have in dictionary
        markup.add(types.InlineKeyboardButton(text=f'{person["name"]} {person["surname"]}', callback_data=f'selected_person_{person["_id"]}'))
    bot.send_message(chat_id=message.chat.id, text=f'The persons have been found: ', parse_mode='html', reply_markup=markup)

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
            text += f"<b>{key}</b>: {value}\n"
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


bot.infinity_polling()
