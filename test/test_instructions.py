import sys

sys.path.append("src/")
from simulator import Simulator
from assembler import assemble_to_numerical
from assembler_utils import twos_complement
from memory import Memory
from utils import f_to_b, b_to_f

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
    # r3 = 00000000000000000000000000000001
    # r2 = 00000000000000000000000000000010
    # ---------------------------------------
    # r1 = 11111111111111111111111111111100
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 0b11111111111111111111111111111100)

def test_xor():
    tester = SingleInstructionSimulator("xor $r1 $r2 $r3")
    # r3 = 00000000000000000000000000000011
    # r2 = 00000000000000000000000000000010
    # ---------------------------------------
    # r1 = 00000000000000000000000000000001
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 0b00000000000000000000000000000001)

def test_xor_negative():
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

def test_addi_negative():
    tester = SingleInstructionSimulator("addi $r5 $r3 -234")
    for _ in range(5):
        tester.step()
    # r5 = -231;
    assert((tester.R[5] - 2**32) == -231)

def test_slti_negative_taken():
    # Test when slti condition is taken          -7 <? -6
    tester = SingleInstructionSimulator("slti $r5 $r3 -6")
    tester.R[3] = -7
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == 1)

def test_slti_negative_not_taken():
    # Test when slti condition is taken         3 <? -6
    tester = SingleInstructionSimulator("slti $r5 $r3 -6")
    for _ in range(5):
        tester.step()
    assert(tester.R[5] == 0)

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
    assert(tester.R[5] == 0)

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
    tester = SingleInstructionSimulator("sub $r1 $r3 $r2")
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == 3 - 2)

def test_sub_negative():
    tester = SingleInstructionSimulator("sub $r1 $r3 $r2")
    # r3 = -100;
    tester.R[3] = twos_complement(100, 32) # r3 = -100;
    tester.R[2] = 50 # $r2 = 50
    expected = twos_complement(150, 32) # $r3 - $r2 = -150
    for _ in range(5):
        tester.step()
    assert(tester.R[1] == expected)

def test_mult():
    tester = SingleInstructionSimulator("mult $r5 $r6")
    tester.R[5], tester.R[6] = 0xFFFFFFFF, 0x12345678
    # 0xFFFFFFFF * 0x12345678 = 0x12345677edcba988

    # 6 cycles because mult takes 2 cycles to complete
    for _ in range(6):
        tester.step()
    assert(tester.LO == (0xedcba988))
    assert(tester.HI == (0x12345677))

def test_muls():
    tester = SingleInstructionSimulator("mul.s $f4 $f5 $f6")
    tester.F[5], tester.F[6] = f_to_b(5.5), f_to_b(10.0)

    print(f_to_b(tester.F[4]))
    # 6 cycles because mul.s takes 6 cycles to complete
    for _ in range(11):
        tester.step()
    print(f_to_b(tester.F[4]))
    assert(tester.F[4] == f_to_b(55.0))

def test_divs():
    tester = SingleInstructionSimulator("div.s $f4 $f5 $f6")
    tester.F[5], tester.F[6] = f_to_b(5.5), f_to_b(5.5)

    # 6 cycles because div.s takes 24 cycles to complete
    for _ in range(29):
        tester.step()
    assert(tester.F[4] == f_to_b(1.0))

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

def test_ls():
    tester = SingleInstructionSimulator("l.s $f1 10($r0) ")
    tester.memory_heirarchy[0].data[10] = f_to_b(4.5)
    for _ in range(5):
        tester.step()
        
    assert(tester.F[1] == f_to_b(4.5))

def test_ss():
    tester = SingleInstructionSimulator("s.s $f1 10($r0)")
    for _ in range(4):
        tester.step()
    assert(tester.memory_heirarchy[0].data[10] == tester.F[1])

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

def test_adds():
    
    tester = SingleInstructionSimulator("add.s $f1 $f2 $f3")
    tester.F[1] = f_to_b(4.0)
    tester.F[2] = f_to_b(4.0)
    tester.F[3] = f_to_b(2.0)
    for _ in range(8):
        tester.step()
    assert(tester.F[1] == f_to_b(b_to_f(tester.F[2]) + b_to_f(tester.F[3])))
    
def test_subs():
        
    tester = SingleInstructionSimulator("sub.s $f1 $f2 $f3")
    tester.F[1] = f_to_b(3.0)
    tester.F[2] = f_to_b(4.0)
    tester.F[3] = f_to_b(2.0)
    print(tester.F[1], tester.F[2], tester.F[3])
    for _ in range(8):
        tester.step()
    assert(tester.F[1] == f_to_b(b_to_f(tester.F[2]) - b_to_f(tester.F[3])))
    
def test_ceqs_true():
    tester = SingleInstructionSimulator("c.eq.s $f1 $f2")
    tester.F[1] = f_to_b(4.0)
    tester.F[2] = f_to_b(4.0)
    for _ in range(3):
        tester.step()
    assert(tester.CC == True)  
    
def test_ceqs_false():
    tester = SingleInstructionSimulator("c.eq.s $f1 $f2")
    tester.F[1] = f_to_b(4.0)
    tester.F[2] = f_to_b(5.0)
    for _ in range(3):
        tester.step()
    assert(tester.CC == False)
        
def test_cles_true():
    tester = SingleInstructionSimulator("c.le.s $f1 $f2")
    tester.F[1] = f_to_b(4.0)
    tester.F[2] = f_to_b(4.0)
    for _ in range(3):
        tester.step()
    assert(tester.CC == True)  
    
def test_cles_false():
    tester = SingleInstructionSimulator("c.le.s $f1 $f2")
    tester.F[1] = f_to_b(5.0)
    tester.F[2] = f_to_b(4.0)
    for _ in range(3):
        tester.step()
    assert(tester.CC == False)
    
def test_clts_true():
    tester = SingleInstructionSimulator("c.lt.s $f1 $f2")
    tester.F[1] = f_to_b(3.0)
    tester.F[2] = f_to_b(4.0)
    for _ in range(3):
        tester.step()
    assert(tester.CC == True)  
    
def test_clts_false():
    tester = SingleInstructionSimulator("c.lt.s $f1 $f2")
    tester.F[1] = f_to_b(4.0)
    tester.F[2] = f_to_b(4.0)
    for _ in range(3):
        tester.step()
    assert(tester.CC == False)

def test_bc1t_true():
    tester = SingleInstructionSimulator("bc1t 0xFF")
    tester.CC = True
    for _ in range(4):
        print(tester.buffer)
        tester.step()
    print(tester.buffer)
    assert(tester.PC == 4 * 0xFF + 4)

def test_bc1t_false():
    tester = SingleInstructionSimulator("bc1t 0xFF")
    tester.CC = False
    for _ in range(4):
        tester.step()
    assert(tester.PC == 16)