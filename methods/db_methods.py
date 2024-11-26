
import requests
from telebot import types
from pymongo import MongoClient
import re


def get_database(db_name):
    CONNECTION_STRING = "mongodb://localhost:27017/"
    client = MongoClient(CONNECTION_STRING)
    return client[db_name]


#FInd method for db
def get_count(db_collection):
    return db_collection.count_documents({})


def add_person(db_collection):
    count_d = get_count(db_collection)
    data = {
        "name": f"name{count_d + 1}",
        "surname": f"surname{count_d + 1}"
    }
    db_collection.insert_one(data)
    return data


def search(db_collection, text_filter):
    #pattern for searching filter, like text + any digit, ignoring cases
    regex = re.compile(f"^{text_filter}\\d+$", re.IGNORECASE)
    return list(db_collection.find({
        "$or": [{"name": {"$regex": regex}} , {"surname": {"$regex": regex}}]
    }))

