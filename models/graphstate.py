from typing import TypedDict, List, Optional
from models.codestate import CodeState
from models.reviewstate import ReviewState

class GraphState(TypedDict):
    error: str
    messages: List[str]
    generation: CodeState
    iterations: int
    success: bool
    code_review: Optional[ReviewState] = None
    spec: str