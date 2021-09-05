import motor.motor_asyncio
from config import Config
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import ssl

mongo = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO, ssl_cert_reqs=ssl.CERT_NONE)

db : Database = mongo["SJBots"]
users : Collection = db["RemoveBGBot"]


class Data:

    async def add_new_user(user_id : int):
        await users.insert_one({'user_id':user_id})

    async def count_users():
        results = await users.count_documents(filter={})
        return results

    async def is_in_db(user_id):
        results = await users.find_one({'user_id':user_id})
        if results == None:
            return False
        else:
            return True

    async def get_user_ids():
        user_ids = []
        results = users.find()
        async for result in results:
            user_ids.append(result['user_id'])

        return user_ids