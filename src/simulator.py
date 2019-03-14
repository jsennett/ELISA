import logging
from memory import Memory, Cache

class Simulator:

    def __init__(self):
        # Default values
        self.pipeline = [None, None, None, None, None]

        DRAM = Memory(lines=2**12, delay=100)
        L1 = Cache(lines=8, words_per_line=1, delay=1, associativity=1, next_level=DRAM, name="L1")
        L2 = Cache(lines=32, words_per_line=1, delay=1, associativity=1, next_level=L1, name="L2")
        self.memory_heirarchy = [L1, L2, DRAM]
        self.cycle = 0
        self.R = [0] * 32 # Integer registers
        self.F = [0] * 32 # Float registers
        self.PC = 0
        self.instructions = []

    def step(self):
        logging.info("Simulator: step()")

        self.cycle += 1

        # TODO: Correctly update PC based on instruction.
        self.PC += 4

        # TODO: start the pipeline chain of events
        pass