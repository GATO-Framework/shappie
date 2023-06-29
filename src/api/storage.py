import dataclasses
import datetime
import typing

import motor.motor_asyncio

import model


class DataStore:
    def __init__(self, url: str, db_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self._db: motor.motor_asyncio.AsyncIOMotorDatabase = self._client[db_name]
        self._messages = self._get_collection("messages")
        self._modes = self._get_collection("modes")
        self._constitutions = self._get_collection("constitutions")
        self._personas = self._get_collection("personas")
        self._state = self._get_collection("state")

    def _get_collection(self, collection_name: str):
        return self._db[collection_name]

    async def save_message(self, message: model.Message):
        payload = dataclasses.asdict(message)
        await self._messages.insert_one(payload)

    async def get_mode(self, name: str) -> model.Mode | None:
        doc = await self._modes.find_one({"name": name})
        if doc:
            return model.Mode(
                name=doc["name"],
            )
        else:
            return None

    async def list_modes(self) -> typing.AsyncIterable[model.Mode]:
        async for doc in self._modes.find():
            yield model.Mode(
                doc["name"],
            )

    async def get_constitution(self, name: str) -> model.Constitution | None:
        doc = await self._constitutions.find_one({"name": name})
        if doc:
            return model.Constitution(
                name=doc["name"],
                components=doc["components"],
            )
        else:
            return None

    async def list_constitutions(self) -> typing.AsyncIterable[model.Constitution]:
        async for doc in self._constitutions.find():
            yield model.Constitution(
                name=doc["name"],
                components=doc["components"],
            )

    async def add_persona(self, persona: model.Persona):
        payload = dataclasses.asdict(persona)
        await self._personas.insert_one(payload)

    async def update_persona(self, persona: model.Persona):
        await self._personas.update_one(
            {"name": persona.name},
            {"$set": {"description": persona.description}},
        )

    async def delete_persona(self, name: str):
        await self._personas.delete_one({"name": name})

    async def get_persona(self, name: str) -> model.Persona | None:
        doc = await self._personas.find_one({"name": name})
        if doc:
            return model.Persona(
                name=doc["name"],
                description=doc["description"],
            )
        else:
            return None

    async def list_personas(self) -> typing.AsyncIterable[model.Persona]:
        async for doc in self._personas.find():
            yield model.Persona(
                doc["name"],
                doc["description"],
            )

    async def get_messages_statistics(
            self,
            start_time: datetime.datetime,
            end_time: datetime.datetime,
    ) -> list[dict]:
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

        messages = []
        async for doc in self._messages.aggregate(pipeline):
            messages.append(dict(
                year=doc["_id"]["year"],
                month=doc["_id"]["month"],
                day=doc["_id"]["day"],
                num_messages=doc["num_messages"],
            ))

        return messages

    async def get_state(self) -> model.State | None:
        pipeline = [
            {
                "$lookup": {
                    "from": "modes",
                    "localField": "mode",
                    "foreignField": "name",
                    "as": "mode"
                }
            },
            {"$unwind": "$mode"},
            {"$unwind": "$constitutions"},
            {
                "$lookup": {
                    "from": "constitutions",
                    "localField": "constitutions",
                    "foreignField": "name",
                    "as": "constitutions"
                }
            },
            {"$unwind": "$constitutions"},
            {
                "$lookup": {
                    "from": "personas",
                    "localField": "persona",
                    "foreignField": "name",
                    "as": "persona"
                }
            },
            {"$unwind": "$persona"},
            {
                "$lookup": {
                    "from": "mutations",
                    "localField": "mutation",
                    "foreignField": "name",
                    "as": "mutation"
                }
            },
            {"$unwind": {
                "path": "$mutation",
                "preserveNullAndEmptyArrays": True
            }},
            {
                "$group": {
                    "_id": "$_id",
                    "mode": {"$first": "$mode"},
                    "constitutions": {"$push": "$constitutions"},
                    "persona": {"$first": "$persona"},
                    "mutation": {"$first": "$mutation"},
                }
            },
        ]

        cursor = self._state.aggregate(pipeline)
        doc = await cursor.to_list(length=1)
        print("***", doc)
        if not doc:
            return None

        doc = doc[0]

        return model.State(
            mode=model.Mode(
                name=doc["mode"]["name"],
            ),
            constitutions=[
                model.Constitution(
                    name=constitution["name"],
                    components=constitution["components"],
                )
                for constitution in doc["constitutions"]
            ],
            persona=model.Persona(
                name=doc["persona"]["name"],
                description=doc["persona"]["description"],
            ),
            mutation=None if not doc["mutation"] else model.Mutation(
                name=doc["mutation"]["name"],
                effect=doc["mutation"]["effect"],
            ),
        )

    async def update_state(self, mode: str, constitutions: list[str], persona: str):
        await self._state.update_one(
            {},
            {
                "$set": {
                    "mode": mode,
                    "constitutions": constitutions,
                    "persona": persona,
                },
            },
        )
