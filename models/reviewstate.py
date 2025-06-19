from pydantic import BaseModel, Field
from typing import Optional

class ReviewState(BaseModel):
    """Model for a review of code and tests generated from a Given-When-Then specs."""
    code_review: Optional[str] = Field(description="The review of the code and tests generated from a Given-When-Then specs if needed.")