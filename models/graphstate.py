from typing import TypedDict, List
from models.codestate import CodeState

class GraphState(TypedDict):
    error: str
    messages: List[str]
    generation: CodeState
    iterations: int
    success: bool