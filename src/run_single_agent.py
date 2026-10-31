"""runs the single-agent baseline"""

from smolagents.utils import AgentGenerationError
from agents.agent_setup import build_single_agent


def main():
    agent = build_single_agent()
    task = input("enter a coding task: ")

    try:
        result = agent.run(task)
    except AgentGenerationError as error:
        result = (
            "STOPPED: model/API error. "
            "Generated files may exist, but completion is unconfirmed.\n"
            + str(error)
        )

    print("\nfinal result:")
    print(result)


if __name__ == "__main__":
    main()