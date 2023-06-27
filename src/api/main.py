import os
import typing

import strawberry
import uvicorn as uvicorn
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

import model.persona
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
class Persona:
    name: str
    description: str


@strawberry.type
class Query:
    @strawberry.field
    async def persona(self, info: Info, name: str) -> typing.Optional[Persona]:
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


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_persona(self, info: Info, name: str, description: str) -> Persona:
        data_store: storage.DataStore = info.context["data_store"]
        persona = model.persona.Persona(name, description)
        await data_store.add_persona(persona)
        return persona

    @strawberry.mutation
    async def update_persona(self, info: Info, name: str,
                             description: str) -> typing.Optional[Persona]:
        data_store: storage.DataStore = info.context["data_store"]
        persona = model.persona.Persona(name=name, description=description)
        await data_store.update_persona(persona)
        updated_persona = await data_store.get_persona(name)
        if updated_persona:
            return updated_persona
        else:
            return None


app = FastAPI()
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)