"""
really basic agent setup

single agent:
user -> coder

multi agent:
user -> orchestrator -> coder <-> tester
"""

import os

from smolagents import ToolCallingAgent, OpenAIModel

from agents.coordinator import Coordinator
from agents.agent_prompts import CODER, TESTER, SINGLE
from tools.agent_toolsets import CODER_TOOLS, TESTER_TOOLS


def build_model():
    return OpenAIModel(
        model_id="openai/gpt-oss-120b",
        api_base="https://api.groq.com/openai/v1",
        api_key=os.environ["GROQ_API_KEY"],
        reasoning_effort="low",
        max_tokens=2048,
        temperature=0.1,
    )

# def build_model():
#     return OpenAIModel(
#         model_id="llama-3.3-70b-versatile",
#         api_base="https://api.groq.com/openai/v1",
#         api_key=os.environ["GROQ_API_KEY"], 
#         max_tokens=2048,
#         temperature=0.1,
#     ) 
# def build_model():
#     return OpenAIModel(
#         model_id="qwen/qwen3.8-27b",
#         api_base="https://api.groq.com/openai/v1",
#         api_key=os.environ["GROQ_API_KEY"],
#         max_tokens=2048,
#         temperature=0.1,
#     )

    # one model is enough for this basic version
    # llm = LiteLLMModel(
    #     model_id="ollama_chat/qwen2.5-coder:1.5b",
    #     api_base="http://localhost:11434",
    #     api_key="anything",
    #     num_ctx=8192
    # )


def build_single_agent():
    
    # Combine existing tools without duplicate tool names.
    tools = {
        tool.name: tool
        for tool in CODER_TOOLS + TESTER_TOOLS
    }

    return ToolCallingAgent(
        tools=list(tools.values()),
        model=build_model(),
        name="single_agent",
        max_steps=16,
        instructions=SINGLE,
    )    


    # agent = ToolCallingAgent(
    #     tools=CODER_TOOLS,
    #     model=llm,
    #     instructions=(
    #         "You are a simple coding agent. "
    #         "Use the file tools to make the code. "
    #         "Run the code with execute_file. "
    #         "If it fails, look at the error, fix it, and try again. "
    #         "Stop when it works or you cant keep going."
    #     )
    # )

    # return agent


def build_multi_agent_system():

  
    llm = build_model()



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


    return Coordinator(coder, tester)



    # for worker in (coder, tester):
    #     worker.prompt_templates["managed_agent"]["task"] = COMPACT_MANAGED_TASK


    # # orchestrator just sends work between the other two
    # orchestrator = ToolCallingAgent(
    #     tools=[],
    #     model=llm,
    #     managed_agents=[
    #         coder,
    #         tester
    #     ],
    #     instructions=ORCHESTRATOR,
    #     max_steps=7,
    # )

    # for agent in orchestrator.managed_agents.values():
    #     agent.inputs.pop("additional_args", None)

    # return orchestrator
