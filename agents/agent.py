from typing import Dict, Any
from executors import PyDockerExecutor
from models.codestate import CodeState
from models.graphstate import GraphState
from langchain.chat_models import init_chat_model
from prompts import get_fix_prompt
import logging

class PyExecutorAgent:
    def __init__(self, model, model_provider, output_formatting):
        self.log = logging.getLogger("PyExecutorAgent")
        self.py_executor = PyDockerExecutor()
        self.ouput_formatting = output_formatting
        self.llm = init_chat_model(model, temperature=0.6, model_provider=model_provider)

    def __del__(self):
        self.py_executor.stop_and_remove()

    def execute_python_with_docker(self, state: GraphState) -> Dict[str, Any]:
        """Execute Python code in a Docker Container"""
        self.log.info("\n\n\n+++++++++++ executing execute_python_with_docker")
        self.py_executor.build_application_structure(state)
        exec_result = self.py_executor.run_script(state)
        print(f"=========s exec_result: {exec_result}")
        return exec_result

    def generate(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n+++++++++++ executing generate")
        generation = self.llm.with_structured_output(CodeState).invoke(state['messages'])
        return {**state,
                "generation": generation,
                "iterations": state["iterations"] + 1}

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

    def fix_code(self, state: GraphState) -> GraphState:
        self.log.info("\n\n\n++++++++++++ executing fix_code")
        # print(f"======== state['error']: {state['error']}, messages: {state['messages']}")
        state['messages'].append(("user", get_fix_prompt(state, self.ouput_formatting)))
        generation = self.llm.with_structured_output(CodeState).invoke(state['messages'])
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
