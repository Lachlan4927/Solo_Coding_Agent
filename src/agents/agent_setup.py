"""
really basic agent setup

single agent:
user -> coder

multi agent:
user -> orchestrator -> coder <-> tester
"""

import os

from smolagents import ToolCallingAgent, OpenAIModel, LiteLLMModel

from agents.coordinator import Coordinator
from agents.agent_prompts import CODER, TESTER, SINGLE
from tools.agent_toolsets import CODER_TOOLS, TESTER_TOOLS, SINGLE_TOOLS

# # good recent build here------------------------
# def build_model():
#     return OpenAIModel(
#         model_id="openai/gpt-oss-120b",
#         api_base="https://api.groq.com/openai/v1",
#         api_key=os.environ["GROQ_API_KEY"],
#         reasoning_effort="low",
#         max_tokens=8192,
#         temperature=0.1,
#         # stop=None,
#     )



def build_model():

    return OpenAIModel(
        model_id="gemini-3.5-flash-lite",
        api_base=(
            "https://generativelanguage.googleapis.com/"
            "v1beta/openai/"
        ),
        api_key=os.environ["GEMINI_API_KEY"],
        max_tokens=8192,
        temperature=0.1,
        reasoning_effort="low",
    )

def build_single_agent():
    


    return ToolCallingAgent(
        tools=SINGLE_TOOLS,
        model=build_model(),
        name="single_agent",
        max_steps=16,
        instructions=SINGLE,
        verbosity_level=2,
     
    )    



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
