from typing import Dict, Any
from executors import PyDockerExecutor
from models.codestate import CodeState
from models.graphstate import GraphState
from models.reviewstate import ReviewState
from langchain.chat_models import init_chat_model
from langchain.output_parsers import PydanticOutputParser
from prompts import get_fix_prompt, get_review_prompt, get_fix_with_review_prompt
import logging
from pydantic_core import ValidationError

class PyExecutorAgent:
    def __init__(self, model, model_provider, output_formatting, try_tolerance=5):
        self.log = logging.getLogger("PyExecutorAgent")
        self.py_executor = PyDockerExecutor()
        self.output_formatting = output_formatting
        self.llm = init_chat_model(model, temperature=0.6, model_provider=model_provider)
        self.try_tolerance = try_tolerance

    def __del__(self):
        self.py_executor.stop_and_remove()

    def execute_python_with_docker(self, state: GraphState) -> Dict[str, Any]:
        """Execute Python code in a Docker Container"""
        self.log.info("\n\n\n+++++++++++ executing execute_python_with_docker")
        try:
            self.py_executor.build_application_structure(state)
            exec_result = self.py_executor.run_script(state)
        except Exception as e:
            self.log.error(f"Exception caught while executing python with docker: {e}")
            exec_result = {"error": str(e)}
        
        print(f"=========s exec_result: {exec_result}")
        return exec_result

    def generate(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n+++++++++++ executing generate")
        
        generation = None
        tries = 0
        while not generation and tries < self.try_tolerance:
            try:
                generation = self.llm.with_structured_output(CodeState).invoke(state['messages'])
            except Exception as e:
                self.log.error(f"Exception caught in generate: {e}.\nRetrying...")
                generation = None
                tries += 1
                
        if not generation:
            self.log.error(f"Failed to generate code and tests correctly within {self.try_tolerance} tries. Not producing code.")
            self.py_executor.stop_and_remove()
            exit(1)
        
        return {**state,
                "generation": generation,
                "iterations": state["iterations"] + 1}

    def validate_generation(self, state: GraphState) -> str:
        self.log.info(f"\n\n+++++++++++++++ executing validate_generation. type(state): {type(state)}")
        generation: CodeState = state['generation']
        if generation and generation.code_module_name and generation.code_under_test and generation.code_under_test_name and generation.filename_extension and generation.test_suite:
            return "pass"
        return "fail"

    # Need to pass the resulting code error output to the llm to evaluate and create a fix if necessary
    def code_check(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n+++++++++++++++ executing code_check")
        # print(f"generation type: {type(state['generation'])}")
        #print(f"checking code for generation: {state['generation']}")
        result = self.execute_python_with_docker(state)
        print(f"============ in code_check, result: {result}")
        return {**state, 
                "error": result.get("error", "no"),
                "success": False if "error" in result else True}

    def review_code(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n++++++++++++ executing review_code")
        parser = PydanticOutputParser(pydantic_object=ReviewState)
        output_formatting = parser.get_format_instructions()
        state["messages"].append(("user", get_review_prompt(state, output_formatting)))
        
        result = None
        tries = 0
        while not result and tries < self.try_tolerance:
            try:
                #TODO: Should we verify that result.code_review exists after?
                result = self.llm.with_structured_output(ReviewState).invoke(state['messages'])
            except Exception as e:
                self.log.error(f"Error getting code review: {e}. Retrying...")
                result = None
                tries += 1

        if not result:
            self.log.error(f"Failed to create a code review within {self.try_tolerance} iterations. Not producing code and tests.")
            self.py_executor.stop_and_remove()
            exit(1)

        return {**state,
                "code_review": result.code_review}

    def fix_with_review(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n++++++++++++ executing fix_with_review")
        parser = PydanticOutputParser(pydantic_object=CodeState)
        output_formatting = parser.get_format_instructions()
        state["messages"].append(("user", get_fix_with_review_prompt(state, output_formatting)))
        result = self.llm.with_structured_output(CodeState).invoke(state['messages'])
        return {**state,
                "messages": state['messages'],
                "generation": result}

    def handle_code_review(self, state: GraphState) -> str:
        self.log.info("\n\n\n+++++++++++++++ executing handle_code_review")
        if state["code_review"]:
            return "fail"
        return "pass"

    def fix_code(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n++++++++++++ executing fix_code")
        # print(f"======== state['error']: {state['error']}, messages: {state['messages']}")
        state['messages'].append(("user", get_fix_prompt(state, self.output_formatting)))
        
        generation = None
        tries = 0
        while not generation and tries < self.try_tolerance:
            try:
                generation = self.llm.with_structured_output(CodeState).invoke(state['messages'])
            except ValidationError as e:
                tries += 1
                self.log.error(f"Validation error while parsing llm output: {e}.\nRetrying...")

        if not generation:
            self.log.error(f"Code not fixed within {self.try_tolerance} iterations. Not generating code and tests.")
            self.py_executor.stop_and_remove()
            exit(1)

        return {**state,
                "messages": state['messages'],
                "generation": generation,
                "iterations": state["iterations"] + 1}
    
    def fail(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n+++++++++++++ executing fail")
        self.py_executor.stop_and_remove()
        return state

    def should_retry(self, state: GraphState) -> str:
        self.log.info("\n\n\n+++++++++++ executing should_retry")
        print(f"============ state[error]: {state['error']}")
        if state['error'] == "no":
            print(f"========= returning end")
            return "end"
        else:
            ret_val = "fix" if state['iterations'] < 5 else "gtfo"
            print(f"========= iterations: {state['iterations']}, ret_val: {ret_val}")
            return ret_val
