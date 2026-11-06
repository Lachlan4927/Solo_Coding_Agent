"""
just the tool lists for each agent

kept here so agent_setup doesnt need to know where every single tool came from
"""

from .file_manager import read_file
from .file_manager import write_file
from .file_manager import list_files
from .file_manager import make_directory
from .file_manager import delete_file
from .code_executor import execute_file
from .test_manager import write_test_file



# coder gets the bigger tool set because it actually changes the project
CODER_TOOLS = [
    read_file,
    write_file, # coder ignores prompt to only write code and leave testing to tester, whilst tester is enforced programatically, coder is not, this is a hallucination.
    list_files,
    make_directory,
    delete_file,
    execute_file
]


# tester only needs to look at stuff and run it for now??
TESTER_TOOLS = [
    read_file,
    write_test_file,
    execute_file,
]



SINGLE_TOOLS = [
    read_file,
    write_file, # coder ignores prompt to only write code and leave testing to tester, whilst tester is enforced programatically, coder is not, this is a hallucination.
    list_files,
    make_directory,
    delete_file,
    execute_file,
    write_test_file
]