"""
really basic agent setup

single agent:
user -> coder

multi agent:
user -> orchestrator -> coder <-> tester
"""

from smolagents import ToolCallingAgent
from smolagents import InferenceClientModel

from tools.agent_toolsets import CODER_TOOLS
from tools.agent_toolsets import TESTER_TOOLS


def build_single_agent():

    # one model is enough for this basic version
    model = InferenceClientModel()

    agent = ToolCallingAgent(
        tools=CODER_TOOLS,
        model=model,
        instructions=(
            "You are a simple coding agent. "
            "Use the file tools to make the code. "
            "Run the code with execute_file. "
            "If it fails, look at the error, fix it, and try again. "
            "Stop when it works or you cant keep going."
        )
    )

    return agent


def build_multi_agent_system():

    multi_model = InferenceClientModel()

    # coder does the actual coding stuff
    coder = ToolCallingAgent(
        tools=CODER_TOOLS,
        model=multi_model,
        name="coder",
        description="writes and fixes the code",

        instructions=(
            "Independently check the implementation against the original user task. "
            "Write Python tests using write_test_file and run them using execute_file. "
            "Report which tests passed or failed and explain any mismatch with the task. "
            "Do not edit the implementation files."
        )
    )

    # tester mostly just checks whatever the coder made
    tester = ToolCallingAgent(
        tools=TESTER_TOOLS,
        model=multi_model,
        name="tester",
        description="checks the coders files and sees if they work",
        instructions=(
            "Independently check the implementation against the original user task. "
            "Write Python tests using write_test_file and run them using execute_file. "
            "Report which tests passed or failed and explain any mismatch with the task. "
            "Do not edit the implementation files."
        )
    )

    # orchestrator just sends work between the other two
    orchestrator = ToolCallingAgent(
        tools=[],
        model=multi_model,
        managed_agents=[
            coder,
            tester
        ],
        instructions=(
            "Give the original task to the coder. "
            "Then give the original task and the coder's file paths to the tester. "
            "If tests fail, send the specific failure back to the coder and request a repair. "
            "Repeat testing after a repair. "
            "Finish with the tested result or a clear explanation of why the task failed."
        )
    )

    return orchestrator
