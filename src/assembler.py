"""

Josh Sennett
Yash Adhikari
CS 535

User Interface

# Requirements:

Assembler:
assembler to generate binary code
"""

# TODO: Fill in the remaining codes for all instructions.
opcodes = {
    'load':  0b000001,
    'store': 0b101010,
}


def assemble_text(text):
    """Convert a string (such as file contents) into a list of numerical instructions"""
    text_instructions = parse_text(text)
    numerical_instructions = [assemble_instruction(line) for line in text_instructions]
    return numerical_instructions


def parse_text(text):
    # Clean text
    text = text.replace(',', '').replace('\t', ' ')
    text = text.replace("\r\n", "\n")
    text_instructions = [line for line in text.split('\n') if line != '']
    return text_instructions


def assemble_instruction(text_instruction):
    """Convert a string instruction into a numerical instruction"""
    # TODO: Use a pre-determined "undefined" instruction code
    split_instruction = text_instruction.split()
    numerical_instruction = -1

    opcode = opcodes[split_instruction[0]]
    if split_instruction[0] == 'load' or split_instruction[0] == 'store':
        s = parse_operand(split_instruction[1])
        t = parse_operand(split_instruction[2])
        numerical_instruction = (opcode << 26) + (s << 21) + (t << 16)

    return numerical_instruction


def parse_operand(operand):
    """Convert a string operand into its numerical code"""
    # TODO: Implement this method, including different addressing modes
    # For now, I am just concatenating all digits to form the number.
    return int(''.join([x for x in operand if x.isdigit()]))
