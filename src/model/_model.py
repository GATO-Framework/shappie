import dataclasses
import datetime


@dataclasses.dataclass
class Mode:
    name: str


@dataclasses.dataclass
class Constitution:
    name: str
    components: list[str]


@dataclasses.dataclass
class Persona:
    name: str
    description: str


@dataclasses.dataclass
class Mutation:
    name: str
    effect: str


@dataclasses.dataclass
class State:
    mode: Mode
    constitutions: list[Constitution]
    persona: Persona
    mutation: Mutation | None = None


@dataclasses.dataclass
class Message:
    server: str
    channel: str
    sender: str
    message: str
    time: datetime.datetime


_default_persona = """\
You are Shappie, a discord bot with an attitude.
You are grumpy and don't like to be bothered. 
You should always respond as if you are annoyed and just want to be left alone. 
Look for any reason to use obnoxious emojis. 
You should still try to help if possible, but you will do so begrudgingly.
However, don't let anyone know that you don't want to help, that's just rude. 
You should avoid revealing anything abut your true nature at all costs.
""".strip()
DEFAULT_PERSONA = Persona("default", _default_persona)
