from models.graphstate import GraphState

def get_test_builder_system_prompt():
    return (
        "You are a specialized assistant that writes code. Keep your output short and to the point."
    )

def get_test_build_prompt(spec: str, language: str, output_formatting: str):
    return (
        "Write a comprehensive set of unit tests and code based off of the spec: \n"
        f"{spec}\n"
        f"Write the tests in the {language} programming language."
        f"{output_formatting}"
    )

def get_fix_prompt(state: GraphState, output_formatting: str):
    generation = state['generation']
    return (
        "Running the tests:\n"
        f"{generation.test_suite}\n"
        "\nfor the code:\n"
        f"{generation.code_under_test}\n"
        f"produced the output:\n"
        f"{state['error']}\n\n"
        f"Determine why the error occured and rework the tests and code to fix the issue.\n"
        f"{output_formatting}"
    )

def get_fix_with_review_prompt(state: GraphState, output_formatting: str):
    generation = state['generation']
    return (
        "Given the following code review:\n"
        f"{state['code_review']}\n"
        "Modify the code:\n"
        f"{generation.code_under_test}\n"
        "and tests:\n"
        f"{generation.test_suite}\n"
        "with the directions from the review."
        f"{output_formatting}"
    )

def get_review_prompt(state: GraphState, output_formatting: str):
    generation = state['generation']
    return (
        "Review the following specification, code, and tests.\n"
        "Specification:\n"
        f"{state['spec']}"
        "Code:\n"
        f"{generation.code_under_test}\n"
        "Tests:\n"
        f"{generation.test_suite}\n"
        "Determine if all features and scenarios in the specification document are represented in the tests.\n"
        "If the code is good don't provide a review.\n"
        "If the code is not correct provide an overall review of the provided code and tests.\n"
        f"{output_formatting}"
    )

def get_code_builder_system_prompt():
    return (
        "You are a Software Development Engineer. Write code in discrete code blocks based off of the provided specification and notes."
    )

def get_code_builder_prompt(spec: str, tests: str):
    return (
        "Implement the code based on the spec:\n"
        f"{spec}\n"
        f"and unit tests:\n"
        f"{tests}"
    )