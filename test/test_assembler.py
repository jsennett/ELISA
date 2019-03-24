import sys

sys.path.append("src/")
from assembler import assemble_instruction, assemble_to_numerical, assemble_to_text

def test_integer_file_instruction_parsing():

    with open('test/integer_instructions.asm') as f:
        file_contents = f.read()

    expected = [
        "add $r1 $r2 $r3",
        "addi $r4 $r8 0x123",
        "sub $r1 $r2 $r3",
        "sll $r5 $r6 0x12",
        "srl $r5 $r6 0x12",
        "mult $r3 $r4",
        "div $r3 $r4",
        "and $r1 $r2 $r3",
        "andi $r1 $r2 0x01",
        "or $r1 $r2 $r3",
        "ori $r1 $r2 0x04",
        "xor $r1 $r2 $r4",
        "xori $r1 $r2 0x04",
        "nor $r1 $r2 $r4",
        "beq $r1 $r2 0x1234",
        "bne $r1 $r2 0x1234",
        "bgez $r1 0x1234",
        "blez $r1 0x1234",
        "bgtz $r2 0x4567",
        "bltz $r2 0x4567",
        "j 0x3456",
        "jal 0x3456",
        "jr $r3",
        "slt $r1 $r2 $r3",
        "slti $r1 $r2 0x1234",
        "lw $r1 0x04($r3)",
        "sw $r1 0x04($r3)"
    ]
    assert(assemble_to_text(file_contents) == expected)


def test_integer_file_instruction_assembly():

    with open('test/integer_instructions.asm') as f:
        file_contents = f.read()

    expected = [
        0b00000000010000110000100000100000,
        0b00100001000001000000000100100011,
        0b00000000010000110000100000100010,
        0b00000000000001100010110010000000,
        0b00000000000001100010110010000010,
        0b00000000011001000000000000011000,
        0b00000000011001000000000000011010,
        0b00000000010000110000100000100100,
        0b00110000010000010000000000000001,
        0b00000000010000110000100000100101,
        0b00110100010000010000000000000100,
        0b00000000010001000000100000100110,
        0b00111000010000010000000000000100,
        0b00000000010001000000100000100111,
        0b00010000001000100001001000110100,
        0b00010100001000100001001000110100,
        0b00000100001000010001001000110100,
        0b00011000001000000001001000110100,
        0b00011100010000000100010101100111,
        0b00000100010000000100010101100111,
        0b00001000000000000011010001010110,
        0b00001100000000000011010001010110,
        0b00000000011000000000000000001000,
        0b00000000010000110000100000101010,
        0b00101000010000010001001000110100,
        0b10001100011000010000000000000100,
        0b10101100011000010000000000000100
    ]
    assert(assemble_to_numerical(file_contents) == expected)

def test_instructions_with_labels():

    # This file has labels
    with open('test/jump_to_label_instructions.asm') as f:
        file_contents = f.read()

    expected = ["add $r1 $r2 $r3",  # mem: 0x0
                "j 0x8",            # mem: 0x4
                "add $r1 $r2 $r3"]  # mem: 0x8

    # Test whether label maps to correct memeory address
    assert(assemble_to_text(file_contents) == expected)

def test_add_instruction():
    assert(assemble_instruction("add $r1 $r2 $r3") == 0b00000000010000110000100000100000)

def test_addi_instruction():
    assert(assemble_instruction("addi $r4 $r8 0x123") == 0b00100001000001000000000100100011)

def test_sub_instruction():
    assert(assemble_instruction("sub $r1 $r2 $r3") == 0b00000000010000110000100000100010)

def test_sll_instruction():
    assert(assemble_instruction("sll $r5 $r6 0x12") == 0b00000000000001100010110010000000)

def test_srl_instruction():
    assert(assemble_instruction("srl $r5 $r6 0x12") == 0b00000000000001100010110010000010)

def test_sra_instruction():
    assert(assemble_instruction("sra $r1 $r2 0x2") == 0b00000000000000100000100010000011)

def test_mult_instruction():
    assert(assemble_instruction("mult $r3 $r4") == 0b00000000011001000000000000011000)

def test_div_instruction():
    assert(assemble_instruction("div $r3 $r4") == 0b00000000011001000000000000011010)

def test_and_instruction():
    assert(assemble_instruction("and $r1 $r2 $r3") == 0b00000000010000110000100000100100)

def test_andi_instruction():
    assert(assemble_instruction("andi $r1 $r2 0x01") == 0b00110000010000010000000000000001)

def test_or_instruction():
    assert(assemble_instruction("or $r1 $r2 $r3") == 0b00000000010000110000100000100101)

def test_ori_instruction():
    assert(assemble_instruction("ori $r1 $r2 0x04") == 0b00110100010000010000000000000100)

def test_xor_instruction():
    assert(assemble_instruction("xor $r1 $r2 $r4") == 0b00000000010001000000100000100110)

def test_xori_instruction():
    assert(assemble_instruction("xori $r1 $r2 0x04") == 0b00111000010000010000000000000100)

def test_nor_instruction():
    assert(assemble_instruction("nor $r1 $r2 $r4") == 0b00000000010001000000100000100111)

def test_beq_instruction():
    assert(assemble_instruction("beq $r1 $r2 0x1234") == 0b00010000001000100001001000110100)

def test_bne_instruction():
    assert(assemble_instruction("bne $r1 $r2 0x1234") == 0b00010100001000100001001000110100)

def test_bgez_instruction():
    assert(assemble_instruction("bgez $r1 0x1234") == 0b00000100001000010001001000110100)

def test_blez_instruction():
    assert(assemble_instruction("blez $r1 0x1234") == 0b00011000001000000001001000110100)

def test_bgtz_instruction():
    assert(assemble_instruction("bgtz $r2 0x4567") == 0b00011100010000000100010101100111)

def test_bltz_instruction():
    assert(assemble_instruction("bltz $r2 0x4567") == 0b00000100010000000100010101100111)

def test_j_instruction():
    assert(assemble_instruction("j 0x3456") == 0b00001000000000000011010001010110)

def test_jal_instruction():
    assert(assemble_instruction("jal 0x3456") == 0b00001100000000000011010001010110)

def test_jalr_instruction():
    assert(assemble_instruction("jalr $r2 $r3") == 0b00000000011000000001000000001001)

def test_jr_instruction():
    assert(assemble_instruction("jr $r3") == 0b00000000011000000000000000001000)

def test_slt_instruction():
    assert(assemble_instruction("slt $r1 $r2 $r3") == 0b00000000010000110000100000101010)

def test_slti_instruction():
    assert(assemble_instruction("slti $r1 $r2 0x1234") == 0b00101000010000010001001000110100)

def test_lw_instruction():
    assert(assemble_instruction("lw $r1 4($r3)") == 0b10001100011000010000000000000100)

def test_lb_instruction():
    assert(assemble_instruction("lb $r1 13($r2)") == 0b10000000010000010000000000001101)

def test_sw_instruction():
    assert(assemble_instruction("sw $r1 4($r3)") == 0b10101100011000010000000000000100)

def test_sb_instruction():
    assert(assemble_instruction("sb $r1 13($r2)") == 0b10100000010000010000000000001101)
