from pydantic import BaseModel, Field
from typing import Optional

class ReviewState(BaseModel):
    """Model for a review of code and tests generated from a Given-When-Then specs."""
    code_review: str = Field(description="The review of the code and tests generated from a Given-When-Then specs.")
    passing_review: bool = Field(description="True if no further iteration on the code and tests are needed. False if there is more work needed on the code and tests.")