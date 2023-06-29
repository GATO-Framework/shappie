import datetime
import os

import strawberry
import uvicorn as uvicorn
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

import model
from api import storage


def get_data_store() -> storage.DataStore:
    url = os.environ.get("MONGO_URI")
    db_name = os.environ.get("MONGO_DB_NAME")
    return storage.DataStore(url, db_name)


async def get_context(
        data_store=Depends(get_data_store),
):
    return {
        "data_store": data_store,
    }


@strawberry.type
class Mode:
    name: str


@strawberry.type
class Constitution:
    name: str
    components: str


@strawberry.type
class Persona:
    name: str
    description: str


@strawberry.type
class State:
    mode: Mode
    constitutions: list[Constitution]
    persona: Persona


@strawberry.type
class MessagesPerDay:
    year: int
    month: int
    day: int
    num_messages: int


@strawberry.type
class Query:
    @strawberry.field
    async def state(self, info: Info) -> State | None:
        data_store: storage.DataStore = info.context["data_store"]
        state = await data_store.get_state()
        if state:
            return state

    @strawberry.field
    async def mode(self, info: Info, name: str) -> Mode | None:
        data_store: storage.DataStore = info.context["data_store"]
        doc = await data_store.get_mode(name)
        if doc:
            return Mode(name=doc.name)

    @strawberry.field
    async def modes(self, info: Info) -> list[Mode]:
        data_store: storage.DataStore = info.context["data_store"]
        return [
            Mode(name=doc.name)
            async for doc in data_store.list_modes()
        ]

    @strawberry.field
    async def constitution(self, info: Info, name: str) -> Constitution | None:
        data_store: storage.DataStore = info.context["data_store"]
        doc = await data_store.get_constitution(name)
        if doc:
            return Constitution(name=doc.name, components=doc.components)

    @strawberry.field
    async def constitutions(self, info: Info) -> list[Constitution]:
        data_store: storage.DataStore = info.context["data_store"]
        return [
            Constitution(name=doc.name, components=doc.components)
            async for doc in data_store.list_constitutions()
        ]

    @strawberry.field
    async def persona(self, info: Info, name: str) -> Persona | None:
        data_store: storage.DataStore = info.context["data_store"]
        doc = await data_store.get_persona(name)
        if doc:
            return Persona(name=doc.name, description=doc.description)

    @strawberry.field
    async def personas(self, info: Info) -> list[Persona]:
        data_store: storage.DataStore = info.context["data_store"]
        return [
            Persona(name=doc.name, description=doc.description)
            async for doc in data_store.list_personas()
        ]

    @strawberry.field
    async def message_statistics(
            self,
            info: Info,
            start_time: datetime.datetime,
            end_time: datetime.datetime,
    ) -> list[MessagesPerDay]:
        data_store: storage.DataStore = info.context["data_store"]
        stats = await data_store.get_messages_statistics(start_time, end_time)
        return [
            MessagesPerDay(
                year=stat['year'],
                month=stat['month'],
                day=stat['day'],
                num_messages=stat['num_messages'],
            ) for stat in stats
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_persona(self, info: Info, name: str, description: str) -> Persona:
        data_store: storage.DataStore = info.context["data_store"]
        persona = model.Persona(name, description)
        await data_store.add_persona(persona)
        return persona

    @strawberry.mutation
    async def update_persona(self, info: Info, name: str,
                             description: str) -> Persona | None:
        data_store: storage.DataStore = info.context["data_store"]
        persona = model.Persona(name=name, description=description)
        await data_store.update_persona(persona)
        updated_persona = await data_store.get_persona(name)
        if updated_persona:
            return updated_persona
        else:
            return None

    @strawberry.mutation
    async def update_state(self, info: Info, mode: str, constitutions: list[str],
                           persona: str) -> State | None:
        data_store: storage.DataStore = info.context["data_store"]
        await data_store.update_state(mode, constitutions, persona)
        updated_state = await data_store.get_state()
        if updated_state:
            return updated_state
        else:
            return None


app = FastAPI()
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
