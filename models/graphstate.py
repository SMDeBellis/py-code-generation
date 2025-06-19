from typing import TypedDict, List, Optional
from models.codestate import CodeState

class GraphState(TypedDict):
    error: str
    messages: List[str]
    generation: CodeState
    iterations: int
    success: bool
    code_review: Optional[str]
    spec: str