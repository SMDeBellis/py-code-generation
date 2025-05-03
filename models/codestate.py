from pydantic import BaseModel, Field

class CodeState(BaseModel):
    """Model for a test suite of unit tests and code under test generated from Given-When-Then specs."""
    test_suite: str = Field(description="The test suite class declaration code without markdown formatting.")
    code_under_test: str = Field(description="The code that the test suite is testing.")
    code_module_name: str = Field(description="The import file name for the class identifier of the code that is being tested.")
    code_under_test_name: str = Field(description="The class identifier of the code that is being tested.")
    filename_extension: str = Field(descripiton="The file extension based off of the language type.")