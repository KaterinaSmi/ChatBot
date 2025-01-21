
import requests
from telebot import types
from pymongo import MongoClient
import re


class MongoDB(object):
    def __init__(self):
        self._client = MongoClient("mongodb://localhost:27017/")
        self._db = self._client["about_people"]
        self._collection_people = self._db["people"]
        self._collection_holidays = self._db["holidays"]

    def get_all(self):
        return self._collection_people.find({})

    def get_count(self):
        return self._collection_people.count_documents({})

    #update_one , update_many ({"job": "developer"})
    def get_person_by_id(self, person_id:int):
        person = self._collection_people.find_one({"_id": person_id})
        return person

    def add_person(self):
        count_d = self.get_count()
        data = {
            "_id": count_d + 1,
            "name": f"name{count_d + 1}",
            "surname": f"surname{count_d + 1}"
        }
        self._collection_people.insert_one(data)
        return data


def search_persons(db_collection, text_filter):
    return list(db_collection.find({
        "$or": [{"name": {"$regex": text_filter}} , {"surname": {"$regex": text_filter}}]
    }))

def search_person_by_birthday(db_collection, month: int):
    return list(db_collection.find({"$expr": {"$eq": [{"$month": "$birthday"}, month]}}))


def update_person_field(db_collection, person_id, person_field, new_value):
    result = db_collection.update_one({"_id": person_id}, {'$set': {person_field: new_value}})
    return result


def delete_person_field(db_collection, person_id, person_field):
    db_collection.update_one({"_id": person_id}, {'$unset': {person_field: 0}})


