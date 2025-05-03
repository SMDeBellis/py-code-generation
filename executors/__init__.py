import docker
from docker.errors import NotFound
import os
import sys
import logging
from dotenv import load_dotenv
import tempfile
import shutil
from typing import Dict, Any
from models.graphstate import GraphState

class PyDockerExecutor:
    def __init__(self):
        self.log = logging.getLogger("PyDockerExecutor")
        self.container_name = "pyexecutor"
        self.docker_client = docker.client.from_env()
        self.container = None
        self.temp_dir = None

    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def create_container(self):
        """Create a new Python container that persists for script execution."""
        # Stop and remove existing container if it exists
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.stop()
            container.remove()
            self.log.info(f"Removed existing container: {self.container_name}")
        except NotFound:
            pass
            
        # Create a temporary directory for sharing files with the container
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp()
            self.log.info(f"Created temporary directory: {self.temp_dir}")
            
        # Create the container with the mounted volume
        self.container = self.docker_client.containers.run(
            image=os.environ["PY_DOCKER_IMAGE"],
            name=self.container_name,
            volumes={self.temp_dir: {'bind': '/app', 'mode': 'rw'}},
            working_dir='/app',
            command="tail -f /dev/null",  # Keep container running
            detach=True
        )
        
        self.log.info(f"Created container: {self.container_name} (ID: {self.container.short_id})")
        return self.container
    

    def update_requirements(self, requirements_path=None, requirements_content=None):
        """
        Update the Python packages in the container based on requirements.txt.
        
        Args:
            requirements_path (str, optional): Path to requirements.txt file
            requirements_content (str, optional): Content of requirements.txt as a string
        
        Returns:
            str: Output from pip install command
        """
        if not self.container:
            self.create_container()
            
        requirements_dest = os.path.join(self.temp_dir, "requirements.txt")
        
        # Get requirements content either from file or direct string
        if requirements_path and os.path.exists(requirements_path):
            shutil.copy(requirements_path, requirements_dest)
            self.log.info(f"Copied requirements from {requirements_path}")
        elif requirements_content:
            with open(requirements_dest, 'w') as f:
                f.write(requirements_content)
            self.log.info("Created requirements.txt from provided content")
        else:
            return "No requirements provided"
            
        # Install the requirements
        exit_code, output = self.container.exec_run(
            cmd="pip install -r requirements.txt",
            workdir="/app"
        )
        
        if exit_code != 0:
            self.log.error(f"Error installing requirements: {output.decode()}")
        else:
            self.log.info("Requirements installed successfully")
            
        return output.decode()
    

    def build_application_structure(self, state: GraphState):
        """Copy code to container in a structured way"""
        if not self.container:
            self.create_container()

        if self.temp_dir:
            generation = state['generation']
            
            tests_dest = os.path.join(self.temp_dir, "test_" + generation.code_under_test_name + ".py")
            with open(tests_dest, 'w+') as test_f:
                test_f.write(generation.test_suite)
            self.log.info(f"Wrote to file: {tests_dest}, tests: {generation.test_suite}")

            code_dest = os.path.join(self.temp_dir, generation.code_module_name + ".py")
            with open(code_dest, 'w+') as code_f:
                code_f.write(generation.code_under_test)
            self.log.info(f"Wrote to file: {code_dest}, code: {generation.code_under_test}")
        else:
            self.log.warning("Temp dir does not exist. Cannot write files.")
 

    def run_script(self, *code: str) -> Dict[str, Any]:
        """Run Python code"""
        if not self.container:
            self.create_container()
            
        # Build the command to run the script
        cmd = ["python", "-m", "unittest", "discover"]
    
        # Run the script
        exit_code, output = self.container.exec_run(
            cmd=cmd,
            workdir="/app"
        )
        
        if exit_code != 0:
            return {'error': output.decode()}
        else:
            return {'result': output.decode()}
            
        
    def stop_and_remove(self):
        """Stop and remove the container."""
        if self.container:
            self.container.stop()
            self.container.remove()
            self.log.info(f"Container {self.container_name} stopped and removed")
            self.container = None


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    load_dotenv()
    py_docker_executor = PyDockerExecutor()
    try:
        script = """
print('hello docker')
"""
        output = py_docker_executor.run_script(script)
        print(f"output: {output}")
        py_docker_executor.stop_and_remove()
    except KeyboardInterrupt:
        exit(0)
            

