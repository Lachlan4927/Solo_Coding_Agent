"""
really basic agent setup

single agent:
user -> coder

multi agent:
user -> orchestrator -> coder <-> tester
"""

from smolagents import ToolCallingAgent
from smolagents import LiteLLMModel # 1.5 ok for 1 tool call, calculator ok for 7B modal? multi tool call, very slow on computer.

from smolagents import OpenAIModel # grok api call
import os #remove this line before submission, DEMO PURPOSES ONLY, WONT WORK WITH UI

from tools.agent_toolsets import CODER_TOOLS

from tools.agent_toolsets import TESTER_TOOLS
from agents.agent_prompts import (
    CODER, TESTER, ORCHESTRATOR, COMPACT_MANAGED_TASK
)

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

    # llm = LiteLLMModel(
    #     model_id="ollama_chat/qwen2.5-coder:7b",
    #     api_base="http://localhost:11434",
    #     api_key="anything",
    #     num_ctx=8192
    # )


    llm = OpenAIModel(
        model_id="openai/gpt-oss-120b",
        api_base="https://api.groq.com/openai/v1",
        api_key=os.environ["GROQ_API_KEY"],
        reasoning_effort="low",
        max_tokens=2048,
        temperature=0.1,
    )




    # coder does the actual coding stuff
    coder = ToolCallingAgent(
        tools=CODER_TOOLS,
        model=llm,
        name="coder",
        description="writes and fixes the code",
        max_steps=10,
        instructions=CODER,            
    )

    # tester mostly just checks whatever the coder made
    tester = ToolCallingAgent(
        tools=TESTER_TOOLS,
        model=llm,
        name="tester",
        description="checks the coders files and sees if they work",
        instructions=TESTER,
        max_steps=6,
    )


    for worker in (coder, tester):
        worker.prompt_templates["managed_agent"]["task"] = COMPACT_MANAGED_TASK

    # orchestrator just sends work between the other two
    orchestrator = ToolCallingAgent(
        tools=[],
        model=llm,
        managed_agents=[
            coder,
            tester
        ],
        instructions=ORCHESTRATOR,
        max_steps=7,
    )

    return orchestrator
