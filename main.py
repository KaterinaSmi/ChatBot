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


@bot.message_handler(commands=['search'])
def search_persons(message):
    if len(message.text.split()) < 2:
        bot.send_message(chat_id=message.chat.id, text="Please provide a name or surname to search.")
        return
    text_message = message.text #get all the text of all the command message
    text_filter = text_message.split(" ")[1]
    persons = db_methods.search(db_collection=people_collection, text_filter=text_filter)
    markup = types.InlineKeyboardMarkup()
    for person in persons:
        markup.add(types.InlineKeyboardButton(text=f'{person["name"]} {person["surname"]}', callback_data=f'selected_person_{person["_id"]}'))
    bot.send_message(chat_id=message.chat.id, text=f'The persons have been found: ', parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func = lambda callback: True)
def callback_message(callback):
    if 'selected_person' in callback.data:
        person_id = int(callback.data[16:])
        bot.send_message(callback.message.chat.id, f'<i>The person you are looking for is {person_id}</i>', parse_mode='html')
bot.infinity_polling()

