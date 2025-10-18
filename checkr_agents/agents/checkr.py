#
# A Checkr bridges an Agent with an Oroboro temporal expression evaluator.
#
#   - automatically defined predicates for agent entities
#   - dictionary of defined predicates and operators
#   - manages the advancement of time
#   - loads assertion modules
#   - sets up assertion loggers (ToDo:)
#

import logging

from oroboro import *
import importlib

from checkr_agents import logger # get the logger

class Checkr:
    
    def __init__(self):

        # globals for use in eval
        self.globs = { }

        # dictionary of one-hot instance encodings
        self.flags = { }

        # list of strings: exprs to evaluate
        self.exprs = [ ]

        # oroboro operators to be populated in an assertion module
        self.globs['Event'] = Event
        self.globs['ObserverEvent'] = ObserverEvent
        self.globs['Task'] = Task
        self.globs['Reason'] = Reason
        self.globs['NoReason'] = NoReason
        self.globs['Timeout'] = Timeout
        self.globs['WaitEvent'] = WaitEvent
        self.globs['Status'] = Status

        self.globs['Pred'] = Pred
        self.globs['Firstof'] = Firstof
        self.globs['Once'] = Once
        self.globs['always'] = always
        self.globs['never'] = never
        self.globs['teevent'] = teevent
        self.globs['teeval'] = teeval

        # experimental: populate the flags in the module
        self.globs['flags'] = self.flags

        # the Oroboro runner
        self.oro = Oroboro()

        # the Assertion module and mainfn generator
        self.mod = None
        self.mainfn = None
        

    def set_flag(self, name):
        self.flags[name] = 1

    def clear_flag(self, name):
        self.flags[name] = 0

    def get_flag(self, name):
        return self.flags.get(name, 0)

    def clear_all_flags(self):
        self.flags.clear()
        
    # define in globs table and pass through if module has been loaded
    def define_symbol(self, name, val):
        self.globs[name] = val
        if self.mod:
            setattr(self.mod, name, val)

    # define a predicate that checks the flags table - used by tool calls in agent
    def define_pred(self, name):

        logger.info(f"DEFINE PRED: {name}")

        def fn(d):
            val = self.get_flag(name) == 1
            logger.debug(f"EVALUATING {name} {val} {self.get_flag(name)} {self.flags}")
            return self.get_flag(name) == 1

        fn.__name__ = f"{name}"  # Pred takes this name for logging
        pred = Pred(fn)
        self.define_symbol(name, pred)

        return pred

    #
    # Define an event and place it in the list of symbols so that it is present in the Assertion module.
    # Return it so it can also be called from the Agent context.
    #
    def define_observer_event(self, name):

        logger.debug(f"DEFINE OBSERVER: {name}")

        evt = ObserverEvent(nicename=name)
        self.define_symbol(name, evt)

        return evt

    # post the event and run until t
    def post_and_run(self, t, evt, *args):
        self.oro.post_at(t, evt, *args)
        self.oro.run_until(t)

    def dump(self):
        for name, val in self.globs.items():
            logger.info(f"{name}: {val}")

    def load_spec(self, modspec):
        """
        load the assertion specification
        args:
            modspec: string, ex: "checkr_agents.agents.assertion1:mainfn"
        """

        modpath, mainname = modspec.split(":")

        # self.mod = importlib.__import__(modpath, self.globs, self.globs, fromlist = [ mainname ])
        self.mod = importlib.import_module(modpath)
        logger.info(f"LOADSPEC ASSERTION MODULE:{self.mod}")

        # Populate the namespace of the assertion module dynamically with the Oroboro names
        # This is essentially dynamically importing checkr.globs into the module
        for name, val in self.globs.items():
            setattr(self.mod, name, val)

        # retrieve the main function by name and retain
        self.mainfn = getattr(self.mod, mainname)
        
        # now start it running as a Task
        self.oro.start(self.mainfn)
         
        


# eval evaulates an expression
# exec executes a string as a block of statements
# setattr(obj, name, value)  might work - you can add a method to a object, for example

if __name__ == '__main__':

    import logging
    from checkr_agents import log_to_console
    log_to_console(logging.DEBUG)

    checkr = Checkr()
    checkr.define_pred("foo")
    psmplr = checkr.define_observer_event("psmplr")

    checkr.dump()

    checkr.loadspec("checkr_agents.agents.assertion1:mainfn")

    checkr.oro = Oroboro()

    oroboro.traceoff()
    checkr.oro.loop().debug=False
    
    # checkr.oro.start(checkr.globs.get('mainfn'))
    checkr.oro.start(checkr.mainfn)
    checkr.set_flag("foo")
    checkr.oro.run_until(10)
    checkr.oro.post_at(20, checkr.mod.psmplr)
    checkr.oro.run_until(20)
    checkr.oro.post_at(40, checkr.mod.psmplr)
    checkr.oro.run_until(50)
    

    # retrieve a value from the modules namespace
    print(f"PSMPLR:{getattr(checkr.mod, 'psmplr')}")
    print(f"PSMPLR:{checkr.mod.psmplr}")

    # print(f"PSMPLR:{checkr.globs.get('psmplr')}")
    # checkr.oro.post_at(20, checkr.globs.get('psmplr'))
