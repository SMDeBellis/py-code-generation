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
        f"""# Comprehensive Code Review Implementation Prompt

You are tasked with implementing ALL changes requested in the following code review. Read through the entire review carefully and ensure every single instruction, suggestion, and requirement is addressed.

## Code Review to Implement:
```
{state['code_review']}
```

## Specification Document:
```
{state['spec']}
```

## Current Code to Modify:
```
{generation.code_under_test}
```

## Current Test Suite to Update:
```
{generation.test_suite}
```

## Implementation Requirements:

**CRITICAL: You must implement EVERY instruction from the code review above. This includes:**

1. **Functional Changes**: Implement all requested feature additions, modifications, or removals
2. **Code Quality Improvements**: Apply all suggested refactoring, optimization, and style changes
3. **Bug Fixes**: Address every identified issue, error, or potential problem
4. **Security Enhancements**: Implement all security-related recommendations
5. **Performance Optimizations**: Apply all suggested performance improvements
6. **Documentation Updates**: Add or modify all requested comments, docstrings, and documentation
7. **Test Updates**: Modify existing tests and add new tests as requested in the review
8. **Error Handling**: Implement all suggested error handling and validation improvements
9. **Code Structure**: Apply all architectural and organizational changes
10. **Best Practices**: Implement all coding standard and best practice recommendations

## Verification Checklist:
Before submitting your changes, verify that you have:
- [ ] Read through the ENTIRE code review
- [ ] Identified ALL distinct instructions and requirements
- [ ] Implemented EACH instruction completely
- [ ] Updated both code and tests as specified
- [ ] Ensured no review instruction was overlooked or partially implemented
- [ ] Maintained functionality while implementing all changes

## Output Requirements:
Provide the complete updated code and test suite that fully incorporates every aspect of the code review. If any review instruction seems unclear or contradictory, implement your best interpretation while noting the ambiguity.

**Remember: Partial implementation is not acceptable. Every single point raised in the code review must be addressed in your updated code and tests.**

{output_formatting}"""
    )

def get_review_prompt(state: GraphState, output_formatting: str):
    generation = state['generation']
    return (
        # "Review the following specification, code, and tests.\n"
        # "Specification:\n"
        # f"{state['spec']}"
        # "Code:\n"
        # f"{generation.code_under_test}\n"
        # "Tests:\n"
        # f"{generation.test_suite}\n"
        # "Determine if all features and scenarios in the specification document are represented in the tests.\n"
        # "If the code is good don't provide a review.\n"
        # "If the code is not correct provide an overall review of the provided code and tests.\n"
        # f"{output_formatting}"
        f"""
# Code Review Prompt

You are conducting a comprehensive code review. Analyze the following materials:

## Specification
{state['spec']}

## Implementation
{generation.code_under_test}

## Test Suite
{generation.test_suite}

## Review Instructions

**Primary Task**: Verify that all features, requirements, and scenarios outlined in the specification are properly implemented and tested.

**Review Criteria**:
1. **Specification Coverage**: Are all specified features implemented in the code?
2. **Test Coverage**: Does the test suite validate all specified requirements and edge cases?
3. **Code Quality**: Is the implementation correct, efficient, and maintainable?
4. **Gap Analysis**: What specification elements are missing from either the code or tests?

**Output Guidelines**:
- If the implementation fully satisfies the specification and tests provide complete coverage, respond with: "APPROVED - Implementation meets all specification requirements."
- If issues are found, provide a structured review covering:
  - **Missing Features**: Specification requirements not implemented
  - **Test Gaps**: Scenarios or edge cases not covered by tests
  - **Code Issues**: Bugs, inefficiencies, or quality concerns
  - **Recommendations**: Specific improvements needed

Be specific in your feedback and reference exact specification requirements when identifying gaps.

{output_formatting}
"""
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