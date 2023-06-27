import dataclasses
import typing

import motor.motor_asyncio

import model.message
import model.persona


class DataStore:
    def __init__(self, url, db_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self._db: motor.motor_asyncio.AsyncIOMotorDatabase = self._client[db_name]
        self._messages = self._get_collection("messages")
        self._links = self._get_collection("links")
        self._personas = self._get_collection("personas")

    def _get_collection(self, collection_name: str):
        return self._db[collection_name]

    async def save_message(self, message: model.message.Message):
        payload = dataclasses.asdict(message)
        await self._messages.insert_one(payload)

    async def add_persona(self, persona: model.persona.Persona):
        payload = dataclasses.asdict(persona)
        await self._personas.insert_one(payload)

    async def update_persona(self, persona: model.persona.Persona):
        await self._personas.update_one(
            {"name": persona.name},
            {"$set": {"description": persona.description}},
        )

    async def delete_persona(self, name):
        await self._personas.delete_one({"name": name})

    async def get_persona(self, name) -> typing.Optional[model.persona.Persona]:
        doc = await self._personas.find_one({"name": name})
        if doc:
            return model.persona.Persona(
                name=doc["name"],
                description=doc["description"],
            )
        else:
            return None

    async def list_personas(self) -> typing.AsyncIterable[model.persona.Persona]:
        async for doc in self._personas.find():
            yield model.persona.Persona(
                doc["name"],
                doc["description"],
            )
