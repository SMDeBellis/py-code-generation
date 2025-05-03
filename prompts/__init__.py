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