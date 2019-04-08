import sys

sys.path.append("src/")
from simulator import Simulator
from assembler import assemble_to_numerical
from memory import Memory

class SingleInstructionSimulator(Simulator):
    """A basic simulator used for testing single instructions"""
    def __init__(self, instruction):
        super().__init__()
        DRAM = Memory(lines=2**8, delay=0)
        self.memory_heirarchy = [DRAM]
        instructions, data = assemble_to_numerical(instruction)
        self.set_instructions(instructions)
        self.R = list(range(32))

def test_and():
    tester = SingleInstructionSimulator("and $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] & tester.R[3])

def test_or():
    tester = SingleInstructionSimulator("or $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] | tester.R[3])

def test_nor():
    tester = SingleInstructionSimulator("nor $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == ~(tester.R[2]) & ~(tester.R[3]))

def test_xor():
    tester = SingleInstructionSimulator("xor $r1 $r2 $r3")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == tester.R[2] ^ tester.R[3])

def test_andi():
    tester = SingleInstructionSimulator("andi $r5 $r3 234")
    for count in range(5):
        tester.step()
    assert(tester.R[5] == tester.R[3] & 234)

def test_ori():
    tester = SingleInstructionSimulator("ori $r5 $r3 234")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == (tester.R[3] | 234))

def test_xori():
    tester = SingleInstructionSimulator("xori $r5 $r3 234")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == (tester.R[3] ^ 234))

def test_addi():
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

def test_mult():
    tester = SingleInstructionSimulator("mult $r5 $r6")
    tester.R[5], tester.R[6] = 0xFFFFFFFF, 0x12345678
    # 0xFFFFFFFF * 0x12345678 = 0x12345677edcba988

    # 6 cycles because mult takes 2 cycles to complete
    for _ in range(6):
        tester.step()
    assert(tester.LO == (0xedcba988))
    assert(tester.HI == (0x12345677))

def test_div():
    tester = SingleInstructionSimulator("div $r12 $r13")
    tester.R[12], tester.R[13] = 0xFFFFFFFF, 0x12345678

    # 6 cycles because div takes 2 cycles to complete
    for _ in range(6):
        tester.step()
    assert(tester.LO == (0xFFFFFFFF // 0x12345678))
    assert(tester.HI == (0xFFFFFFFF %  0x12345678))

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

def test_bgez_true():
    tester = SingleInstructionSimulator("bgez $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bgez_false():
    tester = SingleInstructionSimulator("bgez $r1 0xFF")
    tester.R[1] = -1
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_blez_true():
    tester = SingleInstructionSimulator("blez $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_blez_false():
    tester = SingleInstructionSimulator("blez $r1 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_bltz_true():
    tester = SingleInstructionSimulator("bltz $r1 0xFF")
    tester.R[1] = -1
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bltz_false():
    tester = SingleInstructionSimulator("bltz $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_bgtz_true():
    tester = SingleInstructionSimulator("bgtz $r1 0xFF")
    for _ in range(4):
        tester.step()
    assert(tester.PC == 4 * 0xFF + 4)

def test_bgtz_false():
    tester = SingleInstructionSimulator("bgtz $r1 0xFF")
    tester.R[1] = 0
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)

def test_j():
    tester = SingleInstructionSimulator("j 0xaF")
    for _ in range(2):
        tester.step()
    assert(tester.PC == 4 * 0xaF + 4)
    for _ in range(2):
        tester.step()
    assert(tester.buffer[3] == tester.MEM_NOOP)

def test_jal():
    tester = SingleInstructionSimulator("jal 0xaF")
    for _ in range(2):
        tester.step()
    assert(tester.PC == 4 * 0xaF + 4)
    for _ in range(3):
        tester.step()
    assert(tester.R[31] == 4)

def test_jr():
    tester = SingleInstructionSimulator("jr $r20")
    for _ in range(2):
        print(tester.buffer)
        tester.step()
    assert(tester.PC == 20 + 4)
    for _ in range(2):
        tester.step()
    assert(tester.buffer[3] == tester.MEM_NOOP)

def test_jalr():
    tester = SingleInstructionSimulator("jalr $r20 $r8")
    for _ in range(2):
        print(tester.buffer)
        tester.step()
    assert(tester.PC == 8 + 4)
    for _ in range(3):
        tester.step()
    assert(tester.R[20] == 4)

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
    expected = 0b1111101100000000
    # r1 = r10 >> 4
    tester = SingleInstructionSimulator("sra $r1 $r10 4")
    tester.R[10] = input_val
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == expected)

def test_sra_negative():
    input_val = -255
    expected = -16
    tester = SingleInstructionSimulator("sra $r1 $r10 4")
    tester.R[10] = input_val
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == expected)

def test_sra_positive():
    input_val = 0b0111000000000000
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

def test_mflo():
    tester = SingleInstructionSimulator("mflo $r1")
    tester.LO = 0xDEADBEEF
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 0xDEADBEEF)

def test_mfhi():
    tester = SingleInstructionSimulator("mfhi $r1")
    tester.HI = 0xDEADBEEF
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 0xDEADBEEF)

