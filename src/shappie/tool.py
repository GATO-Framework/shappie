import json
import pathlib
import typing
from .tool_utils import arxiv


async def doot():
    return "Shappie do the doot doot!"


async def when_to_meet():
    return ("People in this server have had luck with when2meet: "
            "https://www.when2meet.com/")


async def paper(query):
    results = await arxiv.search(query)
    results = [result for result in results if result["arxiv_link"]]
    return arxiv.format_results(results)


TOOLS = {
    "doot": doot,
    "meeting": when_to_meet,
    "schedule": when_to_meet,
    "paper": paper,
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
