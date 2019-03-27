"""

Josh Sennett
Yash Adhikari
CS 535

ELISA Assembler

For useful documentation on MIPS instructions, see: 
    https://www.eg.bucknell.edu/~csci320/mips_web/
    http://www.cs.ucsb.edu/~franklin/64/lectures/mipsassemblytutorial.pdf

Required next steps:

    Support negative immediates and offsets: this should convert to appropriate size two's complement (16 bits for immediates)
    Assemble floating point instructions
    Documentation

Possible future steps:

    Support sections (.data / .text)
    Add in all MIPS instructions
    Allow labels to refer to variables in .data
    Code validation, helpful error messsages
    Validate keywords (eg labels can be instruction names, registers must be 0-31)
    Change register names to match MIPS naming ($v0, $t0, etc.)
    support syscall command

"""

# Instruction Types
r_type = set(['add', 'sub', 'mult', 'div', 'and', 'or', 'xor', 'nor', 'jalr', 'jr', 'slt', 'sll', 'srl', 'sra'])
i_type = set(['addi', 'andi', 'ori', 'xori', 'beq', 'bne', 'bgez', 'blez', 'bgtz', 'bltz', 'slti', 'lw', 'lb', 'sw', 'sb'])
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
}

function_codes = {
    'add': 0b100000,
    'sub': 0b100010,
    'sll': 0b000000,
    'srl': 0b000010,
    'sra': 0b000011,
    'div': 0b011010,
    'and': 0b100100,
    'or':  0b100101,
    'xor': 0b100110,
    'nor': 0b100111,
    "jalr":0b001001,
    'jr':  0b001000,
    'slt': 0b101010,
    'mult':0b011000,
    'div': 0b011010,
}


def assemble_instruction(text_instruction):
    print('parsing:', text_instruction)
    """Convert a string instruction into a numerical instruction"""
    split_instruction = text_instruction.split()
    numerical_instruction = -1 # error value

    mnemonic = split_instruction[0]
    if mnemonic == "nop": 
        return 0
    opcode = opcodes[mnemonic]

    # If R-Type instruction
    if mnemonic in r_type:

        # Special format for mult/div
        if mnemonic in ['mult', 'div']:
            shift = 0
            s = parse_register(split_instruction[1])
            t = parse_register(split_instruction[2])
            d = 0
            funct = function_codes.get(mnemonic, 0)

        # Special format for logical shifts
        elif mnemonic in ['srl', 'sll', 'sra']:
            s = 0
            t = parse_register(split_instruction[2])
            d = parse_register(split_instruction[1])
            shift = parse_immediate(split_instruction[3], 5)
            funct = function_codes.get(mnemonic, 0)
            
        # Special format for jalr: 
        elif mnemonic == 'jalr':
            s = parse_register(split_instruction[2])
            t = 0
            d = parse_register(split_instruction[1])
            shift = 0
            funct = function_codes.get(mnemonic, 0)

        # Special format for jr
        elif mnemonic == 'jr':
            s = parse_register(split_instruction[1])
            t = 0
            d = 0
            shift = 0
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
            i = parse_immediate(split_instruction[2], 16)
            if mnemonic == 'bgez':
                t = 1
            else:
                t = 0

        # Other instructions use offset, not immediate
        elif mnemonic in ['lw', 'lb', 'sw', 'sb']:
            t = parse_register(split_instruction[1])
            s, i = parse_register_and_shift(split_instruction[2])

        # Certain branch instructions order s before t
        elif mnemonic in ['bne', 'beq']:
            s = parse_register(split_instruction[1])
            t = parse_register(split_instruction[2])
            i = parse_immediate(split_instruction[3], 16)

        # All others follow the same format
        else:
            t = parse_register(split_instruction[1])
            s = parse_register(split_instruction[2])
            i = parse_immediate(split_instruction[3], 16)

        numerical_instruction = (opcode << 26) + (s << 21) + (t << 16) + (i)

    # If J-Type instruction
    elif mnemonic in j_type:

        # TODO: Support parsing labels
        address = parse_immediate(split_instruction[1], 26)
        numerical_instruction = (opcode << 26) + address

    return numerical_instruction


def parse_register_and_shift(operand):
    """Convert string register [+ shift] operand into numerical value.
    Shift must be in decimal format; non-digit characters will be ignored.

    For example: 6($R3): shift=6, reg=3
    """
    # If a shift is specified
    if '(' in operand and ')' in operand:
        shift = int(''.join([x for x in operand[:operand.find('(')] if x.isdigit()]))
        reg = int(''.join([x for x in operand[operand.find('('):operand.find(')')] if x.isdigit()]))

    # If no shift is specified
    else:
        print(operand)
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


def parse_immediate(operand, bits):
    """Convert string operand into numerical value.
    
    For example: #0x1234: immediate = 4660 (decimal)
    """
    # int(X, 0) interprets the integer using hex prefix '0x' 
    # or binary prefix '0b'. Assumes decimal if no prefix.
    n = int(operand, 0)
    if n < 0:
        n = twos_complement(-n, bits)
    return n

def assemble_to_text(text):
    """Parse assembly code to generate text instructions"""
    text = text.replace(',', '').replace('\t', ' ')
    text = text.replace("\r\n", "\n")

    # Split into lines
    lines = text.split('\n')

    # Clean up lines
    lines = [line[:line.find('#')] if line.find('#') >= 0  # Remove comments 
                    else line for line in lines]
    lines = [line for line in lines if line != '']         # Remove empty lines
    lines = [line.strip() for line in lines]               # Strip whitespace

    # First pass: gather labels
    # 'labels' is a mapping of a label to the idx 
    # of the instruction idx following the label
    labels = {}     
    instruction_idx = 0
    lines_without_labels = []
    for line in lines:

        # If label
        if ":" in line:
            labels[line[:line.find(":")]] = instruction_idx

        # If instruction
        else:
            assert(len(lines_without_labels) == instruction_idx)
            lines_without_labels.append(line)
            instruction_idx += 1

    # Second pass: replace labels with memory location
    lines_with_memory_locations = []
    for i, line in enumerate(lines_without_labels):

        # TODO: confirm these are the only conditions where we could use a label.
        # TODO: Correctly calculate branch and jump 
        if line.startswith('j'):
            for label in labels:
                if label in line:
                    line = line.replace(label, str(labels[label]))
                    break
        # If branch
        elif line.startswith('b'):
            for label in labels:
                if label in line:
                    line = line.replace(label, str(labels[label] - i))
                    break

        lines_with_memory_locations.append(line)

    print(lines_without_labels)
    return lines_with_memory_locations


def assemble_to_numerical(text):
    """Convert a string (such as file contents) into a list of numerical instructions"""
    text_instructions = assemble_to_text(text)
    numerical_instructions = [assemble_instruction(line) for line in text_instructions]
    return numerical_instructions

def twos_complement(n, bits):
    """Compute the twos complement of a positive int"""
    if n < 0 or n>= 2**bits:
        raise ValueError
    
    return 2**bits - n