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

def test_add():
    tester = SingleInstructionSimulator("add $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] + tester.R[3])

def test_sub():
    tester = SingleInstructionSimulator("sub $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] - tester.R[3])

def test_beq_true():
    tester = SingleInstructionSimulator("beq $r1 $r1 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_beq_false():
    tester = SingleInstructionSimulator("beq $r1 $r2 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_bne_true():
    tester = SingleInstructionSimulator("bne $r1 $r2 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bne_false():
    tester = SingleInstructionSimulator("bne $r1 $r1 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_sll():
    tester = SingleInstructionSimulator("sll $r3 $r2 2")
    for _ in range(5):
        tester.step()
    assert(tester.R[3] == tester.R[2] << 2)

def test_srl():
    # r1 = (10 >> 2) = 2
    tester = SingleInstructionSimulator("srl $r1 $r10 2")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[10] >> 2)

def test_sra_negative():
    input_val = 0b1011000000000000
    shift = 4
    expected = 0b1111101100000000
    # r1 = r10 >> 4
    tester = SingleInstructionSimulator("sra $r1 $r10 4")
    tester.R[10] = input_val
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == expected)

def test_sra_positive():
    input_val = 0b0111000000000000
    shift = 4
    expected = 0b0000011100000000
    # r1 = r10 >> 4
    tester = SingleInstructionSimulator("sra $r1 $r10 4")
    tester.R[10] = input_val
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == expected)

def test_lw():
    tester = SingleInstructionSimulator("lw $r1 10($r0) ")
    tester.memory_heirarchy[0].data[10] = 0xABCDEF89
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 0xABCDEF89)

def test_sw():
    tester = SingleInstructionSimulator("sw $r1 10($r0)")
    for _ in range(4):
        tester.step()
    assert(tester.memory_heirarchy[0].data[10] == tester.R[1])

def test_lb():
    tester = SingleInstructionSimulator("lb $r1 10($r0) ")
    # Load from address 10 * 4 + 0 = 40 = 0x28, byte 0
    tester.memory_heirarchy[0].data[10] = 0xABCDEF89
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 0x89)

def test_sb():
    tester = SingleInstructionSimulator("sb $r1 10($r2)")
    # Store byte from R1 into line 10, byte # 2
    tester.R[1] = 0xAB
    # Store into address
    for _ in range(4):
        tester.step()
    assert(tester.memory_heirarchy[0].data[10] == 0x00AB0000)

def test_syscall():
    tester = SingleInstructionSimulator("syscall")
    for _ in range(5):
        assert(tester.end_of_program == False)
        tester.step()
    assert(tester.end_of_program == True)
