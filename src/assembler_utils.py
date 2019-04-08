"""

Josh Sennett
Yash Adhikari
CS 535

Assembler Utils

"""

# Instruction Types
r_type = set(['add', 'sub', 'mult', 'div', 'and', 'or', 'xor', 'nor', 'jalr',
              'jr', 'slt', 'sll', 'srl', 'sra', 'add.s', 'sub.s', 'mul.s',
              'div.s', 'cvt.w.s', 'cvt.s.w', 'c.eq.s', 'c.lt.s', 'c.le.s',
              'mfhi', 'mflo'])
i_type = set(['addi', 'andi', 'ori', 'xori', 'beq', 'bne', 'bgez', 'blez',
              'bgtz', 'bltz', 'slti', 'lw', 'lb', 'sw', 'sb', 'l.s', 's.s',
              'bc1t', 'bc1f'])
j_type = set(['j', 'jal'])

# Instruction opcodes
opcodes = {
    "add":  0b000000,
    "addi": 0b001000,
    "sub":  0b000000,
    "sll":  0b000000,
    "srl":  0b000000,
    "sra":  0b000000,
    "mult": 0b000000,
    "div":  0b000000,
    "and":  0b000000,
    "andi": 0b001100,
    "or":   0b000000,
    "ori":  0b001101,
    "xor":  0b000000,
    "xori": 0b001110,
    "nor":  0b000000,
    "beq":  0b000100,
    "bne":  0b000101,
    "bgez": 0b000001,
    "blez": 0b000110,
    "bgtz": 0b000111,
    "bltz": 0b000001,
    "j":    0b000010,
    "jal":  0b000011,
    "jalr": 0b000000,
    "jr":   0b000000,
    "slt":  0b000000,
    "slti": 0b001010,
    "lw":   0b100011,
    "lb":   0b100000,
    "sw":   0b101011,
    "sb":   0b101000,
    "l.s":  0b110001,
    "s.s":  0b111001,
    "add.s": 0b010001,
    "sub.s": 0b010001,
    "mul.s": 0b010001,
    "div.s": 0b010001,
    "cvt.s.w": 0b010001,
    "cvt.w.s": 0b010001,
    "c.eq.s": 0b010001,
    "c.le.s": 0b010001,
    "c.lt.s": 0b010001,
    "bc1t": 0b010001,
    "bc1f": 0b010001,
    "mfhi": 0b000000,
    "mflo": 0b000000
}

function_codes = {
    'add':  0b100000,
    'sub':  0b100010,
    'sll':  0b000000,
    'srl':  0b000010,
    'sra':  0b000011,
    'div':  0b011010,
    'and':  0b100100,
    'or':   0b100101,
    'xor':  0b100110,
    'nor':  0b100111,
    "jalr": 0b001001,
    'jr':   0b001000,
    'slt':  0b101010,
    'mult': 0b011000,
    'div':  0b011010,
    'add.s': 0b000000,
    'sub.s': 0b000001,
    'mul.s': 0b000010,
    'div.s': 0b000011,
    'c.eq.s': 0b110010,
    'c.le.s': 0b111110,
    'c.lt.s': 0b111100,
    'mfhi': 0b010000,
    'mflo': 0b010010
}

register_names = {
    '$zero': 0,
    '$at': 1,
    '$v0': 2,
    '$v1': 3,
    '$a0': 4,
    '$a1': 5,
    '$a2': 6,
    '$a3': 7,
    '$t0': 8,
    '$t1': 9,
    '$t2': 10,
    '$t3': 11,
    '$t4': 12,
    '$t5': 13,
    '$t6': 14,
    '$t7': 15,
    '$s0': 16,
    '$s1': 17,
    '$s2': 18,
    '$s3': 19,
    '$s4': 20,
    '$s5': 21,
    '$s6': 22,
    '$s7': 23,
    '$t8': 24,
    '$t9': 25,
    '$k0': 26,
    '$k1': 27,
    '$gp': 28,
    '$sp': 29,
    '$fp': 30,
    '$ra': 31,
}

def twos_complement(n, bits):
    """Compute the twos complement of a positive int"""
    if n < 0 or n >= 2**bits:
        raise ValueError

    return 2**bits - n
