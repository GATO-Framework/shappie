import dataclasses
import datetime
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

    async def get_messages_statistics(
            self,
            start_time: datetime.datetime,
            end_time: datetime.datetime,
    ) -> list[dict]:
        # Create a pipeline for aggregation
        pipeline = [
            {
                '$match': {
                    'time': {
                        '$gte': start_time,
                        '$lte': end_time,
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$time'},
                        'month': {'$month': '$time'},
                        'day': {'$dayOfMonth': '$time'},
                    },
                    'num_messages': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]

        # Perform the aggregation
        messages = []
        async for doc in self._messages.aggregate(pipeline):
            # Format the date as a string
            year = doc["_id"]["year"]
            month = doc["_id"]["month"]
            day = doc["_id"]["day"]
            time_period = f"{year}-{month:02d}-{day:02d}"
            messages.append(dict(
                time_period=time_period,
                num_messages=doc["num_messages"],
            ))

        return messages
