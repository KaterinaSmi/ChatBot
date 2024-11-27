
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
        "_id": count_d + 1,
        "name": f"name{count_d + 1}",
        "surname": f"surname{count_d + 1}"
    }
    db_collection.insert_one(data)
    return data


def search(db_collection, text_filter):
    return list(db_collection.find({
        "$or": [{"name": {"$regex": text_filter}} , {"surname": {"$regex": text_filter}}]
    }))

