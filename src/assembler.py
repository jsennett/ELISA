"""

Josh Sennett
Yash Adhikari
CS 535

ELISA Assembler

For useful documentation on MIPS instructions, see:
    https://www.eg.bucknell.edu/~csci320/mips_web/
    http://www.cs.ucsb.edu/~franklin/64/lectures/mipsassemblytutorial.pdf

"""
from assembler_utils import r_type, i_type, j_type, \
    opcodes, function_codes, register_names, twos_complement

import logging
logging.basicConfig(level=logging.WARNING)

def assemble_instruction(text_instruction):
    """Convert text instruction to machine code"""
    print('parsing:', text_instruction)
    """Convert a string instruction into a numerical instruction"""
    split_instruction = text_instruction.split()
    numerical_instruction = -1  # error value

    mnemonic = split_instruction[0]
    if mnemonic == "nop":
        return 0
    elif mnemonic == "syscall":
        return 0b001100

    opcode = opcodes[mnemonic]

    # If R-Type instruction
    if mnemonic in r_type:

        # Floating point ALU
        if mnemonic in ['add.s', 'sub.s', 'mul.s', 'div.s']:
            s = 0b10000
            t = parse_register(split_instruction[3])
            d = parse_register(split_instruction[2])
            shift = parse_register(split_instruction[1])
            funct = function_codes.get(mnemonic)
            print(mnemonic, s, t, d, shift, funct)
            print(mnemonic, bin(s), bin(t), bin(d), bin(shift), bin(funct))

        elif mnemonic == 'cvt.w.s':
            s = 0x10
            t = 0
            d = parse_register(split_instruction[2])
            shift = parse_register(split_instruction[1])
            funct = 0x24

        elif mnemonic == 'cvt.s.w':
            s = 0x14
            t = 0
            d = parse_register(split_instruction[2])
            shift = parse_register(split_instruction[1])
            funct = 0x20

        elif mnemonic in ['c.eq.s', 'c.lt.s', 'c.le.s']:
            s = 0x10
            t = parse_register(split_instruction[2])
            d = parse_register(split_instruction[1])
            shift = 0
            funct = function_codes.get(mnemonic, 0)

        # Special format for mult/div
        elif mnemonic in ['mult', 'div']:
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

        # Special format for mfhi/mflo
        elif mnemonic in ["mfhi", "mflo"]:
            s = 0
            t = 0
            d = parse_register(split_instruction[1])
            shift = 0
            funct = function_codes.get(mnemonic)

        # All others follow the same format
        else:
            s = parse_register(split_instruction[2])
            t, shift = parse_register_and_shift(split_instruction[3])
            d = parse_register(split_instruction[1])
            funct = function_codes.get(mnemonic, 0)

        numerical_instruction = ((opcode << 26) + (s << 21) + (t << 16) +
                                 (d << 11) + (shift << 6) + (funct))

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
        elif mnemonic in ['lw', 'lb', 'sw', 'sb', 'l.s', 's.s']:
            t = parse_register(split_instruction[1])
            s, i = parse_register_and_shift(split_instruction[2])

        # Certain branch instructions order s before t
        elif mnemonic in ['bne', 'beq']:
            s = parse_register(split_instruction[1])
            t = parse_register(split_instruction[2])
            i = parse_immediate(split_instruction[3], 16)

        elif mnemonic in ['bc1t', 'bc1f']:
            s = 0x8
            t = 0 if mnemonic == 'bc1f' else 1
            i = parse_immediate(split_instruction[1], 16)

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
        lp = operand.find('(')
        rp = operand.find(')')
        shift = int(''.join([x for x in operand[:lp] if x.isdigit()]))
        reg = parse_register(operand[lp+1:rp])

    # If no shift is
    else:
        print(operand)
        shift = 0
        reg = int(''.join([x for x in operand if x.isdigit()]))
    return reg, shift


def parse_register(operand):
    """Convert string register operand into numerical value.
    We use conventional MIPS register nicknames. If a nickname is not
    specified or not known, digits are parsed, joined, and cast to int.

    For example:
        '$r3': return 3
        '$a0': return 4
        '12':  return 12
        '1f1': return 11
        '99':  raise ValueError
    """
    # First, see if the register matches a MIPS nickname
    if operand in register_names:
        return register_names[operand]

    # If not, extract digits, join, and integerize.
    else:
        reg = int(''.join([x for x in operand if x.isdigit()]))
        if reg > 31 or reg < 0:
            raise ValueError('Invalid register', reg)
        return reg


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


def parse_data_value(value):
    """Parse the value from a data label. The line will be formatted:

        label: .word 0x123

    The value includes everything after the ":":

        .word 0x123

    Supported data types are:
        .word

    Return integer value
    """
    words = value.split()
    if words[0] not in ['.word']:
        raise ValueError('Invalid data type')

    # Infer data type by prefix (0x -> hex, 0b -> bin, else decimal)
    return int(words[1], 0)


def assemble_to_text(text):
    """Parse assembly code to generate text instructions"""
    text = text.replace(',', '').replace('\t', ' ')
    text = text.replace("\r\n", "\n")

    # Split into lines
    lines = text.split('\n')

    # Clean up lines
    lines = [line[:line.find('#')] if line.find('#') >= 0  # Remove comments
             else line for line in lines]
    lines = [line.strip() for line in lines]               # Strip whitespace
    lines = [line for line in lines if line != '']         # Remove empty lines

    # First pass: gather labels
    # 'labels' is a mapping of a label to the label value
    # Label values are either line number (for subroutines)
    # or data values, based on which section you are in
    # The .text section always comes first.
    current_section = '.text'
    labels = {}
    instruction_idx = 0
    lines_without_labels = []
    for line in lines:

        # If label
        if ":" in line:
            label = line[:line.find(":")]
            value = line[line.find(":") + 1:]
            if current_section == '.text':
                labels[label] = instruction_idx
            elif current_section == '.data':
                labels[label] = parse_data_value(value)
                # After parsing data, continue to next line
                continue

        # If section label
        elif line == '.text':
            # Just skip over the .text section label
            continue
        elif line == '.data':
            current_section = '.data'

        # If  instruction
        else:
            assert(len(lines_without_labels) == instruction_idx)
            lines_without_labels.append(line)
            instruction_idx += 1

    # Second pass: replace labels with memory location
    lines_with_memory_locations = []
    for i, line in enumerate(lines_without_labels):

        # If branch, use relative location
        if line.startswith('b'):
            for label in labels:
                if label in line:
                    line = line.replace(label, str(labels[label] - i))
                    break

        # Otherwise, use absolute location or value
        # TODO: Make sure that all labels should be replaced with this value
        else:
            for label in labels:
                if label in line:
                    line = line.replace(label, str(labels[label]))
                    break

        lines_with_memory_locations.append(line)

    print(lines_without_labels)
    return lines_with_memory_locations


def assemble_to_numerical(text):
    """Convert a string (such as file contents) into a list of
    numerical instructions"""
    text_instructions = assemble_to_text(text)
    numerical_instructions = [assemble_instruction(line)
                              for line in text_instructions]
    return numerical_instructions
