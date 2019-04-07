import sys

sys.path.append("src/")
from simulator import Simulator
from assembler import assemble_to_numerical
from memory import Memory, Cache

class SingleInstructionSimulator(Simulator):
    """A basic simulator used for testing instructions"""
    def __init__(self, instruction):
        super().__init__()
        DRAM = Memory(lines=2**8, delay=0)
        self.memory_heirarchy = [DRAM]
        self.set_instructions(assemble_to_numerical(instruction))
        self.R = list(range(32))

def test_add_instruction():
    tester = SingleInstructionSimulator("add $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] + tester.R[3])

def test_sub_instruction():
    tester = SingleInstructionSimulator("sub $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] - tester.R[3])

def test_beq_true_instruction():
    tester = SingleInstructionSimulator("beq $r1 $r1 0xFF")
    for _ in range(4):
        print(tester.PC)
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_beq_false_instruction():
    tester = SingleInstructionSimulator("beq $r1 $r2 0xFF")
    for _ in range(4):
        print(tester.PC)
        tester.step()
    assert(tester.PC == 16)

def test_bne_true_instruction():
    tester = SingleInstructionSimulator("bne $r1 $r2 0xFF")
    for _ in range(4):
        print(tester.PC)
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bne_false_instruction():
    tester = SingleInstructionSimulator("bne $r1 $r1 0xFF")
    for _ in range(4):
        print(tester.PC)
        tester.step()
    assert(tester.PC == 16)


