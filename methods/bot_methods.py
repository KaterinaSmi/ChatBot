import requests
from telebot import TeleBot

user_handler = {}


#continue asking data
def handle_message(bot: TeleBot, message):
    user_id = message.chat.id
    user_data = user_handler.get(user_id, {'step' : 'start', 'data': {}})

    step = user_data['step']
    data = user_data['data']

    if step == 'name' :
        data['name'] = message.text # saving name
        user_data['step'] = 'surname'
        bot.send_message(user_id, text="Type in your surname")

    if step =='surname' :
        data['surname'] = message.text
        user_data['step'] = 'image'
        bot.send_message(user_id, text="Send your image")

    if step == 'image' :
        data['image'] = ''
        user_data['step'] = 'completed'
        bot.send_message(user_id, text="Thank you! The data has been saved ")


