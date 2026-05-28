from app.runtime.registry import registry
from app.tools.calculator import CalculatorTool
from app.tools.weather import WeatherTool
from app.tools.file_reader import FileReaderTool
from app.tools.web_search import WebSearchTool
from app.tools.sql_query import SQLQueryTool

def register_all_tools():
    registry.register_tool(CalculatorTool())
    registry.register_tool(WeatherTool())
    registry.register_tool(FileReaderTool())
    registry.register_tool(WebSearchTool())
    registry.register_tool(SQLQueryTool())
