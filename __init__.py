import os
import logging
from os import path
import argparse
from langchain.output_parsers import PydanticOutputParser
from prompts import get_test_build_prompt, get_code_builder_prompt, get_test_builder_system_prompt
from agents.agent import PyExecutorAgent, GraphState
from models.codestate import CodeState
from typing import Optional
from dotenv import load_dotenv
import sys
import time
from langgraph.graph import StateGraph, START, END
from datetime import datetime

os.makedirs('log', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'log/py-code-generator-{timestamp}.log'

logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
logging.getLogger('httpcore.http11').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Optional: also log to console
    ]
)
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("Service")
load_dotenv()

def run_code_builder(spec_file: str, language: str):
    with open(spec_file) as f:
        # Prompt the test builder to build tests providing
        spec = f.read()
        parser = PydanticOutputParser(pydantic_object=CodeState)
        output_formatting = parser.get_format_instructions()
        test_builder_prompt = get_test_build_prompt(spec, language, output_formatting)

        log.debug(f"Prompting test builder with user prompt: {test_builder_prompt}")
        agent = PyExecutorAgent(os.getenv('MODEL'), os.getenv('PROVIDER'), output_formatting)

        graph = StateGraph(GraphState)
        graph.add_node("generate", agent.generate)
        graph.add_node("validate_genereration", agent.validate_generation)
        graph.add_node("code_check", agent.code_check)
        graph.add_node("fix_code", agent.fix_code)
        graph.add_node("review_code", agent.review_code)
        graph.add_node("fix_with_review", agent.fix_with_review)
        graph.add_node("fail", agent.fail)
        graph.add_edge(START, "generate")
        graph.add_edge("fail", END)

        graph.add_conditional_edges("generate", agent.validate_generation,
                                    {"fail": "generate", "pass": "code_check"})
        graph.add_conditional_edges("code_check", agent.should_retry,
                                    {"fix": "fix_code", "gtfo": "fail", "end": "review_code"})
        graph.add_conditional_edges("fix_code", agent.validate_generation,
                                    {"fail": "fix_code", "pass": "review_code"})
        graph.add_conditional_edges("review_code", agent.handle_code_review,
                                    {"pass": END, "fail": "fix_with_review"})
        graph.add_conditional_edges("fix_with_review", agent.validate_generation,
                                    {"fail": "fix_with_review", "pass": "code_check"})

        app = graph.compile()

        results = None

        while not results or not results['success'] or not results['generation']:
            results = app.invoke({"messages": [
            ("system", get_test_builder_system_prompt()),
            ("user", test_builder_prompt)],
                    "iterations": 0,
                    "error": "",
                    "generation": None,
                    "success": False,
                    "code_review": None,
                    "spec": spec},
                    config={"recursion_limit": 100})
        
        log.info(f"Code creation has completed. results: {results}")
        if results and results['generation']:
            result = results['generation']
            output_dir_name = f"build/tests-{str(time.time())}/"
            os.makedirs(output_dir_name)

            if result.filename_extension:
                file_extension = result.filename_extension
            else:
                file_extension = ".txt"

            if result.test_suite:
                with open(f"{output_dir_name}/tests{file_extension}", "+w") as test_file:
                    log.debug(f"type(result.test_suite): {type(result.test_suite)}")
                    if result.test_suite:
                        test_file.write(f"{result.test_suite}\n")

                if result.code_under_test:
                    if result.code_module_name:
                        code_file_name = result.code_module_name
                    else:
                        code_file_name = "code"

                    with open(f"{output_dir_name}/{code_file_name}{file_extension}", "+w") as code_file:
                        if result.code_under_test:
                            code_file.write(f"{result.code_under_test}\n")
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-c',
        '--create-workspace',
        type=str,
        help='Create a workspace to build the application from the given argument.'
    )
    group.add_argument(
        '-l',
        '--load-workspace',
        type=str,
        help='Workspace to work from and to activate the environment.'
    )
    group.add_argument(
        '-s',
        '--specification',
        type=str,
        help='Specification to build application from.'
    )
    parser.add_argument(
        '--language',
        type=str,
        default='Python',
        help='The programming language to develop in. Defaults to the greatest programming language ever! All Hail!'
    )

    args = parser.parse_args()
    
    if args.create_workspace is not None:
        # run the workspace creation algorithm
        pass

    if args.load_workspace is not None:
        #run the workspace load algorithm
        pass

    if args.specification is not None:
        if not path.exists(args.specification):
            log.error(f"Specification file {args.specification} not found. Exiting.")
            exit(1)


        #begin the chaos
        run_code_builder(args.specification, args.language) 
