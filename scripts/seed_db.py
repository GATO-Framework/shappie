import asyncio
import json

import motor.motor_asyncio


class DatabaseSeeder:
    def __init__(self, url: str, db_name: str, layer_file: str,
                 persona_file: str, message_file: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self._db = self._client[db_name]
        self._layer_file = layer_file
        self._persona_file = persona_file
        self._message_file = message_file

    async def seed(self):
        if not await self._needs_seeding():
            print("Database already seeded. Exiting...")
            return

        await self._clear_database()
        await self._insert_personas()
        await self._insert_messages()
        await self._insert_layers()

    async def _clear_database(self):
        for collection_name in ("personas", "messages", "layer-info"):
            await self._db[collection_name].drop()

    async def _needs_seeding(self) -> bool:
        return not await self._db["personas"].find_one()

    async def _insert_personas(self):
        with open(self._persona_file, 'r') as f:
            personas = json.load(f)
            await self._db['personas'].insert_many(personas)

    async def _insert_messages(self):
        with open(self._message_file, 'r') as f:
            messages = json.load(f)
            await self._db['messages'].insert_many(messages)

    async def _insert_layers(self):
        with open(self._layer_file, 'r') as f:
            messages = json.load(f)
            await self._db['layer-info'].insert_many(messages)


def seed_db():
    # Change the parameters as per your requirements
    seeder = DatabaseSeeder(
        url="mongodb://localhost:27017",
        db_name="GATO",
        persona_file="../data/seed/GATO.personas.json",
        message_file="../data/seed/GATO.messages.json",
        layer_file="../data/seed/GATO.layer-info.json",
    )

    # Run the seeder
    asyncio.run(seeder.seed())


if __name__ == '__main__':
    seed_db()
