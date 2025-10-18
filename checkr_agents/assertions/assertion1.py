#
# An assertion that watches the default events
#

import logging

logger = logging.getLogger("assertion1")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('assertion1.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def watch_on_add_tool():
    while True:
        yield WaitEvent(on_add_tool)
        logger.info(f"ON_ADD_TOOL {on_add_tool.val}")

def watch_on_add_instruction():
    while True:
        yield WaitEvent(on_add_instruction)
        logger.info(f"ON_ADD_INSTRUCTION {on_add_instruction.val}")


def watch_on_query_received():
    while True:
        yield WaitEvent(on_query_received)
        logger.info(f"ON_QUERY_RECEIVED {on_query_received.val}")
        
def watch_on_query_analyzed():
    while True:
        yield WaitEvent(on_query_analyzed)
        logger.info(f"ON_QUERY_ANALYZED {on_query_analyzed.val}")

def watch_on_one_tool_called():
    while True:
        yield WaitEvent(on_one_tool_called)
        logger.info(f"ON_ONE_TOOL_CALLED {on_one_tool_called.val}")

def watch_on_all_tools_called():
    while True:
        yield WaitEvent(on_all_tools_called)
        logger.info(f"ON_ALL_TOOLS_CALLED {flags}")

def watch_on_tool_calls_analyzed():
    while True:
        yield WaitEvent(on_tool_calls_analyzed)
        logger.info(f"ON_TOOL_CALLS_ANALYZED {on_tool_calls_analyzed.val}")
        
def watch_on_query_handled():
    while True:
        yield WaitEvent(on_query_handled)
        logger.info(f"ON_QUERY_HANDLED {on_query_handled.val}")
        

def mainfn(oro):

    print(f"ASSERTION1:{logger}")

    logger.info(f"ASSERTION1: MAINFN STARTING")

    # spawn the subtasks
    t00 = Task(watch_on_add_tool)
    t01 = Task(watch_on_add_instruction)
    
    t10 = Task(watch_on_query_received)
    t11 = Task(watch_on_query_analyzed)

    t20 = Task(watch_on_one_tool_called)
    t21 = Task(watch_on_all_tools_called)
    t22 = Task(watch_on_tool_calls_analyzed)

    t12 = Task(watch_on_query_handled)

    yield NoReason()
    

    
