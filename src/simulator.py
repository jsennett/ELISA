import logging

class Simulator:

    def __init__(self):
        self.pipeline = []
        self.memory_heirarchy = None
        self.cycle = 0

        self.R = [0] * 32 # Integer registers
        self.F = [0] * 32 # Float registers

    def step(self):
        logging.info("Simulator: step()")
        self.cycle += 1
        # Todo: start the pipeline chain of events
        pass