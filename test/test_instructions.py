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

def test_and_instruction():
    tester = SingleInstructionSimulator("and $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] & tester.R[3])

def test_or_instruction():
    tester = SingleInstructionSimulator("or $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] | tester.R[3])

def test_nor_instruction():
    tester = SingleInstructionSimulator("nor $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == ~(tester.R[2]) & ~(tester.R[3]))

def test_xor_instruction():
    tester = SingleInstructionSimulator("xor $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] ^ tester.R[3])

def test_andi_instruction():
    tester = SingleInstructionSimulator("andi $r5 $r3 234")
    for count in range(5):
        tester.step()
    assert(tester.R[5] == tester.R[3] & 234)

def test_ori_instruction():
    tester = SingleInstructionSimulator("ori $r5 $r3 234")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == (tester.R[3] | 234))

def test_xori_instruction():
    tester = SingleInstructionSimulator("xori $r5 $r3 234")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == (tester.R[3] ^ 234))

def test_addi_instruction():
    tester = SingleInstructionSimulator("addi $r5 $r3 234")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == (tester.R[3] + 234))

def test_slti_instruction_taken():
    # Test when slti condition is taken
    tester = SingleInstructionSimulator("slti $r5 $r3 6")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == 1)

def test_slti_instruction_not_taken():
    # Test when slti condition is NOT taken
    tester = SingleInstructionSimulator("slti $r5 $r3 2")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == 5)
    
def test_slt_instruction_taken():
    # Test when slt condition is taken
    tester = SingleInstructionSimulator("slt $r5 $r3 $10")
    for _ in range(5):
        tester.step()
    print(tester.R)
    assert(tester.R[5] == 1)

def test_slt_instruction_not_taken():
    # Test when slt condition is NOT taken
    tester = SingleInstructionSimulator("slt $r5 $r3 $2")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == 5)

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

def test_mult_instruction():
    tester = SingleInstructionSimulator("mult $r5 $r6")
    # stall because of mult
    for _ in range(6):
        tester.step()
    assert(tester.lo == (tester.R[5]*tester.R[6]) & 0xFFFFFFFF)
    assert(tester.hi == (tester.R[5]*tester.R[6]) >> 32)

def test_div_instruction():
    tester = SingleInstructionSimulator("div $r13 $r12")
    # stall because of div
    for _ in range(6):
        tester.step()
    assert(tester.lo == (tester.R[13]//tester.R[12]))
    assert(tester.hi == (tester.R[13]%tester.R[12]))
    
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

def test_bgez_true_instruction():
    tester = SingleInstructionSimulator("bgez $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bgez_false_instruction():
    tester = SingleInstructionSimulator("bgez $r1 0xFF")
    tester.R[1] = -1
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_blez_true_instruction():
    tester = SingleInstructionSimulator("blez $r1 0xFF")
    tester.R[1] = 0    
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_blez_false_instruction():
    tester = SingleInstructionSimulator("blez $r1 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_bltz_true_instruction():
    tester = SingleInstructionSimulator("bltz $r1 0xFF")
    tester.R[1] = -1   
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bltz_false_instruction():
    tester = SingleInstructionSimulator("bltz $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)
    
def test_bgtz_true_instruction():
    tester = SingleInstructionSimulator("bgtz $r1 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bgtz_false_instruction():
    tester = SingleInstructionSimulator("bgtz $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)
    
def test_j_instruction():
    tester = SingleInstructionSimulator("j 0xaF")
    for _ in range(2):
        tester.step()
    assert(tester.PC == 4 * 0xaF + 4)
    for _ in range(2):
        tester.step()
    assert(tester.buffer[3] == tester.MEM_NOOP)
    
def test_jal_instruction():
    tester = SingleInstructionSimulator("jal 0xaF")
    for _ in range(2):
        tester.step()
    assert(tester.PC == 4 * 0xaF + 4)
    for _ in range(3):
        tester.step()
    assert(tester.R[31] == 4)

def test_jr_instruction():
    tester = SingleInstructionSimulator("jr $r20")
    for _ in range(2):
        print(tester.buffer)
        tester.step()
    assert(tester.PC == 20 + 4)
    for _ in range(2):
        tester.step()
    assert(tester.buffer[3] == tester.MEM_NOOP)
    
def test_jalr_instruction():
    tester = SingleInstructionSimulator("jalr $r20 $r8")
    for _ in range(2):
        print(tester.buffer)
        tester.step()
    assert(tester.PC == 8 + 4)
    for _ in range(3):
        tester.step()
    assert(tester.R[20] == 4)