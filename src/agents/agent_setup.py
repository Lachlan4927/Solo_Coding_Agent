"""
really basic agent setup

single agent:
user -> coder

multi agent:
user -> orchestrator -> coder <-> tester
"""

from smolagents import ToolCallingAgent
from smolagents import LiteLLMModel

from tools.agent_toolsets import CODER_TOOLS
from tools.agent_toolsets import TESTER_TOOLS


def build_single_agent():

    # one model is enough for this basic version
    llm = LiteLLMModel(
        model_id="ollama_chat/qwen2.5-coder:1.5b",
        api_base="http://localhost:11434",
        api_key="anything",
        num_ctx=8192
    )

    agent = ToolCallingAgent(
        tools=CODER_TOOLS,
        model=llm,
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

    llm = LiteLLMModel(
        model_id="ollama_chat/qwen2.5-coder:1.5b",
        api_base="http://localhost:11434",
        api_key="anything",
        num_ctx=8192
    )

    # coder does the actual coding stuff
    coder = ToolCallingAgent(
        tools=CODER_TOOLS,
        model=llm,
        name="coder",
        description="writes and fixes the code",

        instructions=(
            "You are the Coder agent. "
            "Make exactly one tool call per response. "
            "You may only use these tools: read_file, write_file, list_files, "
            "make_directory, delete_file, execute_file, and final_answer. "
            "Never invent or create a new tool name. "
            "To create a Python file, call write_file with path and content. "
            "For example, to create calculator.py, call write_file with "
            "path set to calculator.py and content set to the complete Python code. "
            "After each tool call, stop and wait for its result. "
            "Never output multiple Action blocks or JSON objects together. "
            "Implement the complete original user task. "
            "Use read_file and list_files when you need to inspect existing files. "
            "Use write_file to create or change implementation files. "
            "write_file automatically creates missing folders. "
            "Use execute_file to run the finished Python implementation. "
            "If execution fails, inspect the error and repair the implementation. "
            "Only finish after execute_file succeeds or you cannot continue. "
            "In your final answer, list every implementation file you created or changed "
            "and report the execution result. "
            "Do not write test files because testing belongs to the Tester."
        )
    )

    # tester mostly just checks whatever the coder made
    tester = ToolCallingAgent(
        tools=TESTER_TOOLS,
        model=llm,
        name="tester",
        description="checks the coders files and sees if they work",
        instructions=(
            "You are the Tester agent. "
            "Make exactly one tool call per response. "
            "After each tool call, stop and wait for its result. "
            "Never output multiple Action blocks or JSON objects together. "
            "Independently check the implementation against the original user task. "
            "Use read_file to inspect the implementation files. "
            "Use write_test_file to create Python tests. "
            "Test files run from the tests folder, so add /workspace to sys.path "
            "before importing implementation files. "
            "Use execute_file to run the test file. "
            "Do not edit implementation files. "
            "Report which requirements were tested and which tests passed or failed. "
            "Finish with exactly TEST_RESULT: PASS when every required test passes. "
            "Finish with exactly TEST_RESULT: FAIL when a test fails, evidence is missing, "
            "or the implementation does not meet the original task."
        )
    )

    # orchestrator just sends work between the other two
    orchestrator = ToolCallingAgent(
        tools=[],
        model=llm,
        managed_agents=[
            coder,
            tester
        ],
        instructions=(
            "You are the Orchestrator agent. "
            "Make exactly one managed-agent call per response. "
            "After each call, stop and wait for its result. "
            "You may only call coder, tester, or final_answer. "
            "Never call python_interpreter, write files, or execute code yourself. "
            "First call coder with the complete original user task. "
            "After coder returns, call tester with the original task, "
            "the implementation file paths, and the Coder's execution result. "
            "You must not call final_answer before the Tester returns a result. "
            "If the Tester reports TEST_RESULT: FAIL, call coder again with the exact "
            "test failures and request a repair. "
            "After every repair, call tester again. "
            "Stop after three coding attempts. "
            "Only call final_answer when the Tester reports TEST_RESULT: PASS, "
            "or when three attempts have failed. "
            "The final answer must accurately report whether the tests passed."
        )
    )

    return orchestrator
