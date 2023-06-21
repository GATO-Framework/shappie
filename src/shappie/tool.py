import typing


def doot():
    return "Shappie do the doot doot!"


TOOLS = {
    "doot": doot
}


class ToolCollection:
    def __init__(self):
        self._tools = {}

    def __len__(self):
        return len(self._tools)

    def schema(self):
        pass

    def add_tool(self, tool_name: str):
        tool = TOOLS[tool_name]
        self._tools[tool_name] = tool

    def get_tool(self, tool_name) -> typing.Callable:
        return self._tools[tool_name]
