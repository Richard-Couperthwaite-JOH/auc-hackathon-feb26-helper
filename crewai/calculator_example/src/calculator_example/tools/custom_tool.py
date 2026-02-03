from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class calculation_input(BaseModel):
    """Input schema for calculation tools."""
    number1: str = Field(..., description="First number to be processed.")
    number2: str = Field(..., description="Second number to be processed.")

class addition_tool(BaseTool):
    name: str = "Addition Tool"
    description: str = (
        "Take the input numbers and return their sum as a string."
    )
    args_schema: Type[BaseModel] = calculation_input

    def _run(self, number1: str, number2: str) -> str:
        sum_out = int(number1) + int(number2)
        return str(sum_out)
    
class multiplication_tool(BaseTool):
    name: str = "Multiplication Tool"
    description: str = (
        "Take the input numbers and return their product as a string."
    )
    args_schema: Type[BaseModel] = calculation_input

    def _run(self, number1: str, number2: str) -> str:
        product_out = int(number1) * int(number2)
        return str(product_out)