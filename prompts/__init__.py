from models.graphstate import GraphState

def get_test_builder_system_prompt():
    return (
        "You are a specialized assistant that writes code. Keep your output short and to the point."
    )

def get_test_build_prompt(spec: str, language: str, output_formatting: str):
    return (
        f"""# Comprehensive Code and Test Implementation from Specification

You are tasked with creating a complete implementation that fully satisfies the following specification. Your implementation must be thorough, correct, and include comprehensive test coverage.

## Specification to Implement:
```
{spec}
```

## Implementation Requirements:

### Code Implementation:
1. **Complete Functionality**: Implement ALL features, functions, classes, and methods described in the specification
2. **Exact Behavior**: Ensure the code behaves exactly as specified for all described scenarios
3. **Input/Output Compliance**: Handle all specified inputs and produce all specified outputs correctly
4. **Edge Cases**: Implement proper handling for boundary conditions and edge cases mentioned in the spec
5. **Error Handling**: Implement all specified error conditions, exceptions, and error messages
6. **Performance Requirements**: Meet any performance criteria specified
7. **Data Structures**: Use appropriate data structures that align with the specification requirements
8. **API Compliance**: If the spec defines an API or interface, implement it exactly as specified

### Test Implementation in {language}:
1. **Complete Coverage**: Write tests for EVERY function, method, and feature described in the specification
2. **Positive Test Cases**: Test all normal operation scenarios described in the spec
3. **Negative Test Cases**: Test all error conditions and invalid inputs mentioned in the spec
4. **Boundary Testing**: Test edge cases, limits, and boundary conditions
5. **Integration Testing**: Test how different components work together as specified
6. **Data Validation**: Test input validation and output verification
7. **Performance Testing**: Include tests for any performance requirements
8. **Regression Testing**: Ensure tests catch any deviation from the specified behavior

### Quality Assurance:
- **Specification Traceability**: Every requirement in the spec should be traceable to code implementation and test coverage
- **Code Quality**: Follow {language} best practices and coding standards
- **Test Quality**: Write clear, maintainable, and reliable tests
- **Documentation**: Include clear comments explaining complex logic and specification compliance

## Pre-Implementation Analysis:
Before writing code, carefully analyze the specification to:
1. Identify all functional requirements
2. Identify all non-functional requirements (performance, security, etc.)
3. Identify all input/output specifications
4. Identify all error conditions and edge cases
5. Determine the appropriate architecture and design patterns
6. Plan the test strategy to ensure complete coverage

## Deliverables:
Provide two complete sections:

### 1. Production Code
- Complete, working implementation that fully satisfies the specification
- Well-structured, maintainable code following {language} best practices
- Comprehensive error handling and input validation
- Clear documentation and comments

### 2. Test Suite
- Comprehensive unit tests covering all functionality
- Tests for all positive and negative scenarios
- Edge case and boundary condition testing
- Clear test organization and naming
- Assertions that verify specification compliance

## Verification Criteria:
Your implementation will be considered complete when:
- [ ] Every requirement in the specification has been implemented
- [ ] Every implemented feature has corresponding tests
- [ ] All specified behaviors are correctly implemented
- [ ] All specified error conditions are properly handled
- [ ] Tests provide comprehensive coverage of the specification
- [ ] Code and tests are production-ready quality

**Critical**: Do not implement partial functionality. The code must fully satisfy the entire specification, and the tests must comprehensively verify all specified behavior.

{output_formatting}"""
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