import asyncio
import json
import pathlib

import motor.motor_asyncio


class DatabaseSeeder:
    def __init__(self, url: str, db_name: str, layer_dir: str,
                 persona_file: str, message_file: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self._db = self._client[db_name]
        self._layer_dir = layer_dir
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
        layer_files = pathlib.Path(self._layer_dir).glob('*.md')
        layers = []

        for layer_file in layer_files:
            with open(layer_file, 'r') as f:
                layer = {"name": layer_file.stem, "content": f.read()}
                layers.append(layer)

        await self._db['layer-info'].insert_many(layers)


def seed_db():
    # Change the parameters as per your requirements
    seeder = DatabaseSeeder(
        url="mongodb://localhost:27017",
        db_name="GATO",
        layer_dir="layers",
        persona_file="GATO.personas.json",
        message_file="GATO.messages.json",
    )

    # Run the seeder
    asyncio.run(seeder._clear_database())


if __name__ == '__main__':
    seed_db()
