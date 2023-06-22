import discord
import motor.motor_asyncio


class DataStore:
    def __init__(self, url, db_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self._db: motor.motor_asyncio.AsyncIOMotorDatabase = self._client[db_name]

    def _get_collection(self, collection_name: str):
        return self._db[collection_name]

    async def save_message(self, message: discord.Message):
        logs = self._get_collection("logs")
        await logs.insert_one({
            "server": message.guild.name,
            "channel": message.channel.name,
            "sender": message.author.name,
            "message": message.content,
            "time": message.created_at,
        })

    async def save_link(self, message: discord.Message):
        links = self._get_collection("links")
        await links.insert_one({
            "server": message.guild.name,
            "channel": message.channel.name,
            "sender": message.author.name,
            "link": message.content,
            "time": message.created_at,
        })
