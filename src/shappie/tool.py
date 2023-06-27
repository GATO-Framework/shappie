import json
import pathlib
import random
import typing


def doot():
    choices = [
        "5nqw7zaTNnwOpnhfWh",
        "3s81dTaNAQbvg0IxWy",
        "26uf7RJZkFVj7zRqE",
        "v9PnwTVN3JPad3xchA",
        "UU7lo24DP8YsU",
        "aGrvdgvnK6F4JrOqkI",
    ]
    gif = random.choice(choices)
    gif_url = f"https://media.giphy.com/media/{gif}/giphy.gif"
    context = f"Say something silly like 'doot doot the dootly doot 🔥'"
    return dict(
        context=context,
        use_llm=True,
        image_url=gif_url,
    )


def when_to_meet():
    content = "People in this server have had luck with `when2meet`."
    return dict(
        content=content,
        use_llm=False,
        url="https://www.when2meet.com/",
    )


def get_layer_info(layer: int):
    path = pathlib.Path("data") / "layers" / f"layer-{layer}.md"
    with open(path) as file:
        context = file.read()
    return dict(
        context=context,
        use_llm=True,
    )


TOOLS = {
    "doot": doot,
    "meeting": when_to_meet,
    "schedule": when_to_meet,
    "layer": get_layer_info,
}


class ToolCollection:
    def __init__(self):
        self._tools: dict[str, typing.Callable] = {}
        self._tools_by_func: dict[str, typing.Callable] = {}

    def __len__(self):
        return len(self._tools)

    def schema(self):
        path = pathlib.Path(__file__).parent / "tool-schema.json"
        with open(path) as file:
            data = json.load(file)
        tool_schema = []
        for tool in set(self._tools.values()):
            tool_schema.append(data[tool.__name__])
        return tool_schema

    def add_tool(self, keyword: str):
        tool = TOOLS[keyword]
        self._tools[keyword] = tool
        self._tools_by_func[tool.__name__] = tool

    def get_tool(self, tool_name) -> typing.Callable:
        return self._tools_by_func[tool_name]
