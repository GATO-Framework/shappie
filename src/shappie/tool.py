import json
import pathlib
import typing


def doot():
    return "You should say something like \"I do the doot doot!\""


def when_to_meet():
    return ("People in this server have had luck with when2meet: "
            "https://www.when2meet.com/")


def get_layer_info(layer: int):
    path = pathlib.Path(__file__).parent.parent / "layers" / f"layer-{layer}.md"
    with open(path) as file:
        return file.read()


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
