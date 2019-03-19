"""

Josh Sennett
Yash Adhikari
CS 535

ELISA Assembler

For useful documentation on MIPS instructions, see: 
    https://www.eg.bucknell.edu/~csci320/mips_web/
"""

# Instruction Types
r_type = set(['add', 'sub', 'mult', 'div', 'and', 'or', 'xor', 'nor', 'jr', 'slt', 'sll', 'srl'])
i_type = set(['addi', 'andi', 'ori', 'xori', 'beq', 'bne', 'bgez', 'blez', 'bgtz', 'bltz', 'slti', 'lw', 'sw'])
j_type = set(['j', 'jal'])

# Instruction opcodes
opcodes = {
    "add":  0b000000,
    "addi": 0b001000,
    "sub":  0b000000,
    "sll":  0b000000,
    "srl":  0b000000,
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
    "jr":   0b000000,
    "slt":  0b000000,
    "slti": 0b001010,
    "lw":   0b100011,
    "sw":   0b101011,
}

function_codes = {
    'add': 0b100000,
    'sub': 0b100010,
    'sll': 0b000000,
    'srl': 0b000010,
    'ult': 0b011000,
    'div': 0b011010,
    'and': 0b100100,
    'or':  0b100101,
    'xor': 0b100110,
    'nor': 0b100111,
    'jr':  0b001000,
    'slt': 0b101010,
    'mult':0b011000,
    'div': 0b011010,
}


def assemble_instruction(text_instruction):
    """Convert a string instruction into a numerical instruction"""
    split_instruction = text_instruction.split()
    numerical_instruction = -1 # error value

    mnemonic = split_instruction[0]
    opcode = opcodes[mnemonic]

    # If R-Type instruction
    if mnemonic in r_type:

        # Special format for mult/div
        if mnemonic in ['mult', 'div']:
            shift = 0
            d = 0
            s = parse_register(split_instruction[1])
            t = parse_register(split_instruction[2])
            funct = function_codes.get(mnemonic, 0)

        # Special format for logical shifts
        elif mnemonic in ['srl', 'sll']:
            s = 0
            d = parse_register(split_instruction[1])
            t = parse_register(split_instruction[2])
            shift = parse_immediate(split_instruction[3])
            funct = function_codes.get(mnemonic, 0)
            
        # Special format for jr
        elif mnemonic == 'jr':
            s = parse_register(split_instruction[1])
            shift = 0
            d = 0
            t = 0
            funct = function_codes.get(mnemonic, 0)

        # All others follow the same format
        else:
            d = parse_register(split_instruction[1])
            s = parse_register(split_instruction[2])
            t, shift = parse_register_and_shift(split_instruction[3])
            funct = function_codes.get(mnemonic, 0)

        numerical_instruction = (opcode << 26) + (s << 21) + (t << 16) + (d << 11) + (shift << 6) + (funct)

    # If I-Type instruction
    elif mnemonic in i_type:

        # Special format for certain branch instructions
        if mnemonic in ['bgez', 'blez', 'bgtz', 'bltz']:
            s = parse_register(split_instruction[1])
            i = parse_immediate(split_instruction[2])
            if mnemonic == 'bgez':
                t = 1
            else:
                t = 0

        # Other instructions use offset, not immediate
        elif mnemonic in ['lw', 'sw']:
            t = parse_register(split_instruction[1])
            s, i = parse_register_and_shift(split_instruction[2])

        # Certain branch instructions order s before t
        elif mnemonic in ['bne', 'beq']:
            s = parse_register(split_instruction[1])
            t = parse_register(split_instruction[2])
            i = parse_immediate(split_instruction[3])

        # All others follow the same format
        else:
            t = parse_register(split_instruction[1])
            s = parse_register(split_instruction[2])
            i = parse_immediate(split_instruction[3])

        numerical_instruction = (opcode << 26) + (s << 21) + (t << 16) + (i)

    # If J-Type instruction
    elif mnemonic in j_type:

        address = parse_immediate(split_instruction[1])
        numerical_instruction = (opcode << 26) + address

    return numerical_instruction


def parse_register_and_shift(operand):
    """Convert string register [+ shift] operand into numerical value

    For example: 6($R3): shift=6, reg=3
    """
    # If a shift is specified
    if '(' in operand and ')' in operand:
        shift = int(''.join([x for x in operand[:operand.find('(')] if x.isdigit()]))
        reg = int(''.join([x for x in operand[operand.find('('):operand.find(')')] if x.isdigit()]))

    # If no shift is specified
    else:
        shift = 0
        reg = int(''.join([x for x in operand if x.isdigit()]))
    return reg, shift


def parse_register(operand):
    """Convert string register operand into numerical value.
    
    For example: $R3: reg=3
    """
    # If specifying a register, return an int of the numerical chars
    if operand[0] in ['$', 'r', 'R', 't', 'T', 'f', 'F']:
        return int(''.join([x for x in operand if x.isdigit()]))
    else:
        print(operand)
        raise ValueError


def parse_immediate(operand):
    """Convert string operand into numerical value.
    
    For example: #0x1234: immediate = 4660 (decimal)
    """
    # int(X, 0) interprets the integer using hex prefix '0x' 
    # or binary prefix '0b'. Assumes decimal if no prefix.
    return int(operand.replace('#', ''), 0)


def assemble_text(text):
    """Convert a string (such as file contents) into a list of numerical instructions"""
    text_instructions = parse_text(text)
    numerical_instructions = [assemble_instruction(line) for line in text_instructions]
    return numerical_instructions


def parse_text(text):
    # Clean text; the only delimiters should be spaces and newlines.
    text = text.replace(',', '').replace('\t', ' ')
    text = text.replace("\r\n", "\n")

    # Split lines, ignoring comments and empty lines
    text_instructions = [line[:line.find('#')] for line in text.split('\n') if line[:line.find('#')] != '']

    return text_instructions