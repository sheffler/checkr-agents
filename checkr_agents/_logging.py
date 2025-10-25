import logging

# Define a logger for use across this package
logger = logging.getLogger("checkr")

# Call this to set up to log to a console handler
def log_to_console(level):

    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('\033[94m%(asctime)s - %(levelname)s\033[0m - %(message)s',
                                  datefmt='%H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    

#
# A function that Assertions can use to set up their logger in a consistent way
#   ex: logger = checkr_agents.assertion_logger("assertion1")
#

def assertion_logger(name: str):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

