from pymongo import MongoClient, database
from typing import Tuple
import os

class DatabaseSession:
    _client: MongoClient
    _db: database.Database

    def __init__(self) -> None:
        self._client = MongoClient(os.getenv('MONGO_URI'), ssl=True)
        print("Connected to MongoDB", self._client.server_info()['version'])
        self._db = self._client.get_database(os.getenv('MONGO_DB'))

    def get_client(self) -> MongoClient:
        return self._client

    def insert(self, collection: str, data: dict) -> Tuple[bool, str]:
        try:
            result = self._db.get_collection(collection).insert_one(data)
            return True, str(result.inserted_id)
        except Exception as e:
            return False, str(e)

    def find(self, collection: str, condition: dict, col_excl: dict = {}, num_rec: int = 10) -> Tuple[bool, list | str]:
        try:
            result = self._db.get_collection(collection).find(condition, col_excl).limit(num_rec)
            if result is None:
                return False, []
            return True, list(result)
        except Exception as e:
            return False, str(e)

    def findOne(self, collection: str, condition: dict, col_excl: dict = {}) -> Tuple[bool, dict | None]:
        try:
            result = self._db.get_collection(collection).find_one(condition, col_excl)
            if result is None:
                return False, None
            return True, result
        except Exception as e:
            return False, str(e)

    def updateOne(self, collection: str, condition: dict, updated_data: dict) -> Tuple[bool, dict]:
        try:
            result = self._db.get_collection(collection).update_one(condition, {"$set": updated_data})
            return True, result
        except Exception as e:
            return False, str(e)

    def update(self, collection: str, condition: dict, updated_data: dict) -> Tuple[bool, dict]:
        try:
            result = self._db.get_collection(collection).update_many(condition, {"$set": updated_data})
            return True, result
        except Exception as e:
            return False, str(e)

    def delete(self, collection: str, condition: dict) -> Tuple[bool, dict]:
        try:
            result = self._db.get_collection(collection).delete_many(condition)
            return True, result
        except Exception as e:
            return False, str(e)

    def deleteOne(self, collection: str, condition: dict) -> Tuple[bool, dict]:
        try:
            result = self._db.get_collection(collection).delete_one(condition)
            return True, result
        except Exception as e:
            return False, str(e)

    def close(self) -> None:
        self._client.close()

    # def __del__(self):
    #     self.close()
    #     print("Connection to MongoDB closed")
