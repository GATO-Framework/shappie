import dataclasses
import datetime


@dataclasses.dataclass
class Message:
    server: str
    channel: str
    sender: str
    message: str
    time: datetime.datetime
