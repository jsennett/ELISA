"""

Josh Sennett
Yash Adhikari
CS 535

Simulator

"""
from memory import Memory, Cache

import logging
logging.basicConfig(level=logging.INFO)


class Simulator:
    """
    Current: Only implements stalls when access to memory does not return a
    value but a response of "wait" and there is a Jump instruction
    In order for simulator to finish processing instructions, need to run Noop
    instructions through the pipeline (0x00000000)

    Notes below from source:
    https://www.ece.ucsb.edu/~strukov/ece154aFall2013/viewgraphs/pipelinedMIPS.pdf

    In MIPS pipeline with a single memory
    – Load/store requires data access
    – Instruction fetch would have to stall for that cycle
    - Would cause a pipeline “bubble”

    Prevent the instructions in the IF and ID stages from
    progressing down the pipeline – done by preventing the PC
    register and the IF/ID pipeline register from changing
        – Hazard detection Unit controls the writing of the PC
        (PC.write) and IF/ID (IF/ID.write) registers

    Data Hazard:
        Can fix data hazard by waiting – stall – but impacts CPI

    Jumps not decoded until ID, so one flush is needed (destroy loaded
    intruction in the IF stage)

    OPCODE / FUNCTION Values:
    https://en.wikibooks.org/wiki/MIPS_Assembly/Instruction_Formats
    """

    def __init__(self):
        logging.info("__init__()")

        # Cycle count
        self.cycle = 1

        # Memory
        DRAM = Memory(lines=2**12, delay=100)
        L2 = Cache(lines=256, words_per_line=4, delay=3, associativity=1, next_level=DRAM, name="L2")
        L1 = Cache(lines=128, words_per_line=4, delay=0, associativity=1, next_level=L2, name="L1")
        self.memory_heirarchy = [L1, L2, DRAM]

        # For convenience, define NOOP format at each stage
        self.IF_NOOP = [0, 0]                 # Fmt: [instruction, PC]
        self.ID_NOOP = [0, 0, 0, 0, 0, 0, 0]  # [op, r, s, t, shift, fnct, PC]
        self.EX_NOOP = [0, 0, 0, 0]           # [opcode, funct, d, value]
        self.MEM_NOOP = [0, 0]                # Fmt: [reg, value]

        # (Re)set values of registers and memory
        self.reset_registers()
        self.reset_memory()

        # Status
        self.status = ""

        # Enable or disable pipelining
        self.pipeline_enabled = True


    def reset_registers(self):
        logging.info("reset_registers()")

        # Whether the program is terminated
        self.end_of_program = False

        # Registers
        self.R = list(range(0, 32))  # Todo: replcae with self.R = [0] * 32
        self.F = [0] * 32

        # TODO: Set PC to where the first instruction is.
        self.PC = 0

        # Create a set of destination registers that need to be updated
        # TODO: see if hi/lo/pc/control registers need to be tracked
        self.R_dependences = set()  # Integer registers
        self.F_dependences = set()  # FP registers

        # Initialize buffer with no-ops
        self.buffer = [self.IF_NOOP, self.ID_NOOP, self.EX_NOOP, self.MEM_NOOP]

    def reset_memory(self):
        logging.info("reset_memory()")
        for level in self.memory_heirarchy:
            level.reset_data()

    def step(self):
        logging.info("step()")
        self.status = ""
        self.WB()
        self.cycle += 1

        logging.info("Cycle {} - {}".format(self.cycle, self.status))
        logging.info("Current buffer contents:", self.buffer)

    def IF(self):
        """Instruction Fetch stage

        Input read from self.memory_heirchy[0]
        Outputs buffer values to self.buffer[0]

        Input:
            [instruction]
            int instruction: machine code instruction

        Output:
            stall: [0, PC]
            operation: [instruction, PC]

        Read from memory at address self.PC (or, line self.PC//4).
        If stalled accessing memory to fetch instruction, stall
          with a noop and do not increment the PC.
        Otherwise, increment the PC by 4.
        """
        logging.info("IF()")
        # Get the instruction to be processed and pass it along to ID stage
        # TODO: Correctly implement when we finish a program.

        # Get instruction from memory
        instruction = self.memory_heirarchy[0].read(self.PC//4) # TODO: read from address rather than line number

        # If stalled on instruction fetch from memory
        if instruction == "wait":
            # Insert noop
            self.buffer[0] = [0, 0]
            self.status = "IF wait to load inst; " + self.status
            return

        # Increment the program counter
        self.PC += 4

        # Pass instruction and PC to the buffer. Note that a NOOP is a sll
        # instruction, so we are not treating it specially
        self.buffer[0] = [instruction[0], self.PC]
        self.status = "IF fetched instruction; " + self.status
        return

    def ID(self):
        """Instruction Decode stage

        Input buffer values from self.buffer[0]
        Outputs buffer values to self.buffer[1]

        Input:
            [instruction, PC]
            int instruction: machine code instruction
            int PC: Program counter at time of instruction fetch

        Output:
            R: [opcode, s, t, d, shift, funct, PC]
            I: [opcode, s, t, immediate, PC]
            J: NOOP; force stall and flush the pipeline
            syscode: [instruction, PC]
            NOOP: [0, 0, 0, 0, 0, 0, PC]

        Note that s, t, d are either register numbers or register values
        depending on the instruction so that the next stages have the
        information needed to work correctly

        """
        logging.info("ID()")

        # If syscall
        if self.buffer[0][0] == 0b001100:
            self.buffer[1] = self.buffer[0].copy()
            self.status = "ID syscall; " + self.status
            self.IF()
            return

        # Decode operation
        current_instruction, PC = self.buffer[0]
        decode_results = []
        opcode = current_instruction >> 26

        # if r: [opcode, s, t, d, shift, funct]
        if opcode == 0:

            s = (current_instruction & 0x03E00000) >> 21
            t = (current_instruction & 0x001F0000) >> 16
            d = (current_instruction & 0x0000F800) >> 11
            shift = (current_instruction & 0x000007C0) >> 6
            funct = (current_instruction & 0x3F)

            # If data dependency then stall - pass a noop and don't call IF
            # r0 cannot be changed, so it should not cause a stall
            if s in self.R_dependences or t in self.R_dependences:
                self.status = "ID data dependency; " + self.status
                self.buffer[1] = self.ID_NOOP.copy()
                return

            else:
                # TODO: use self.F instead of self.R for floating point operations
                decode_results = [opcode, self.R[s], self.R[t], d, shift, funct, PC]
                self.status = "ID R-type decoded; " + self.status

                # Update dependency table. Note that a destination of r0
                # does not cause a dependency since it has a fixed value zero
                if d != 0:
                    self.R_dependences.add(d)

        # If j-type: [opcode, target]
        elif opcode in [2, 3]:
            target = current_instruction & 0x03FFFFFF
            decode_results = [opcode, target, PC]
            self.status = "ID J-type decoded; " + self.status
            # TODO: Think whether we should be updating the PC here for a jump operation

        # If i-type: [opcode, s, t, immediate]
        else:
            s = (current_instruction & 0x03E00000) >> 21
            t = (current_instruction & 0x001F0000) >> 16
            immediate = current_instruction & 0x0000FFFF

            # "Sign extension"
            if (immediate >> 15 == 1):
                immediate = -1*(immediate ^ 0xFFFF)-1

            # If t is a source, use value self.R[t]
            # This includes: beq, bne, sw, sb
            # TODO: As we add more instructions, we need to expand these lists.
            if opcode in [0b000100, 0b000101, 0b101011, 0b101000]:

                # If data dependency then stall - pass a noop
                if s in self.R_dependences or t in self.R_dependences:
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    self.status = "ID I-type decoded; " + self.status
                    decode_results = [opcode, self.R[s], self.R[t], immediate, PC]

            # If t is a destination, use value t
            # This includes: addi, andi, ori, xori, bgez, blez, bgtz, bltz, slti, lw, lb,
            # TODO: As we add more instructions, we need to expand these lists.
            else:

                # If data dependency then stall - pass a noop
                if s in self.R_dependences:
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    self.status = "ID I-type decoded; " + self.status
                    decode_results = [opcode, self.R[s], t, immediate, PC]
                    self.R_dependences.add(t)

        # Update the buffer
        self.buffer[1] = decode_results

        # TODO: Shift this logic into the J-Type section above
        # if j or jal
        if opcode in [0x2, 0x3]:

            # Insert a noop in the previous buffer
            self.buffer[0] = [0, PC]

            # Change the PC based on the jump address
            self.PC = (PC & 0xF0000000) | (target << 2)

        # Either way, call the IF stage.
        self.IF()

    def EX(self):
        """Execute Stage

        Input buffer values from self.buffer[1]
        Outputs buffer values to self.buffer[2]

        Input:
            R: [opcode, s, t, d, shift, funct, PC]
            I: [opcode, s, t, immediate, PC]
            J: NOOP; force stall and flush the pipeline
            syscode: [instruction, PC]

        Output:
            R: [opcode, d, funct, result]
            I:
                load/store: [opcode, t, value]
                branch:     [opcode, target]
            J:
                jal: [opcode, target, PC]
                j:   [opcode, target]

            syscode: [instruction, PC]
            NOOP:    [0, 0, 0, 0]

        """
        logging.info("EX()")

        # If syscall:
        if self.buffer[1][0] == 0b001100:
            self.buffer[2] = self.buffer[1].copy()
            self.status = "EX syscall; " + self.status
            self.ID()
            return

        current_instruction = self.buffer[1].copy()

        # If R-Type
        if current_instruction[0] == 0:
            opcode, s, t, d, shift, funct, PC = current_instruction

            # If Add
            if funct == 0x20:
                execute_results = [opcode, funct, d, s+t]
                self.status = "EX add; " + self.status

            # If Sub
            elif funct == 0x22:
                execute_results = [opcode, funct, d, s-t]
                self.status = "EX sub; " + self.status

            # If sll; note that this also includes noops
            elif funct == 0:
                execute_results = [opcode, funct, d, t << shift]
                self.status = "EX sll; " + self.status

            # TODO: Implement remaining r-type instructions
            else:
                raise ValueError('Unknown funct {:05b} for R-Type with \
                                 opcode: {:06b}'.format(funct, opcode))

        # If J-Type
        elif current_instruction[0] in [0x2, 0x3]:
            opcode, target, PC = current_instruction

            # TODO: Confirm PC is correct
            # If JAL
            if opcode == 0x3:
                execute_results = [opcode, target, PC]

            # If J
            elif opcode == 0x2:
                execute_results = [opcode, target]

            # TODO: Implement remaining j-type instructions
            else:
                raise ValueError('Unknown J-Type opcode {:06b}'.format(opcode))

        # If I-Type
        else:
            opcode, s, t, immediate, PC = current_instruction

            # If t is a source, use value self.R[t]
            # This includes: sw, sb, lw, lb
            if opcode in [0b101011, 0b101000, 0b100011, 0b100000]:
                execute_results = [opcode, t, s + (immediate << 2)]
                self.status = "EX lw or sw; " + self.status

            # BEQ
            elif opcode == 0b000100:
                # If branch is taken
                if s == t:
                    execute_results = [opcode, PC - 4 + (immediate << 2)]
                    self.status = "EX beq, taken; " + self.status
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    self.status = "EX beq, not taken; " + self.status
                    execute_results = self.EX_NOOP.copy()

            # BNE
            elif opcode == 0b000101:
                # If branch is taken
                if s != t:
                    execute_results = [opcode, PC - 4 + (immediate << 2)]
                    self.status = "EX bne taken; " + self.status
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    execute_results = self.EX_NOOP.copy()
                    self.status = "EX bne, not taken; " + self.status

            # TODO: Implement remaining r-type instructions
            else:
                raise ValueError("Unknown opcode for I-Type instruction: {}".format(opcode))

        self.buffer[2] = execute_results
        self.ID()

    def MEM(self):
        """Memory Stage

        Input buffer values from self.buffer[2]
        Outputs buffer values to self.buffer[3]
          May read from, or write to memory

        Input:
            R: [opcode, d, funct, result]
            I:
                load/store: [opcode, t, value]
                branch:     [opcode, target]
            J:
                jal: [opcode, target, PC]
                j:   [opcode, target]

            syscode: [instruction, PC]
            NOOP:    [0, 0, 0, 0]

        Output:

            syscode: [instruction, PC]



        """
        logging.info("MEM()")
        # The memory stage accesses the main memory. It first attempts to get
        # the write or read from cache within 1 clock cycle (changable),
        # and if it cannot, a stall is incurred

        # If syscall
        if self.buffer[2][0] == 0b001100:
            self.buffer[3] = self.buffer[2].copy()
            self.status = "MEM syscall; " + self.status
            self.EX()
            return

        current_instruction = self.buffer[2].copy()

        # If lw, lb, sw, sb
        if current_instruction[0] in [0b101011, 0b101000, 0b100011, 0b100000]:
            opcode, t, s = current_instruction

            # If sw ("sw $rt offset(base)")
            if opcode == 0b101011:

                # Write to memory
                response = self.memory_heirarchy[0].write(memory_address=s//4, value=t)
                if response == "wait":
                    # insert noop, don't call EX() since MEM is stalled
                    self.buffer[3] = self.MEM_NOOP
                    self.status = "MEM wait to store; " + self.status
                    return
                else:
                    self.buffer[3] = self.MEM_NOOP
                    self.status = "MEM store successful; " + self.status
                    self.EX()
                    return

            # If lw ("lw $rt offset(base)")
            elif opcode == 0b100011:

                # Write to memory
                response = self.memory_heirarchy[0].read(memory_address=s//4)
                if response == "wait":
                    # insert noop, don't call EX() since MEM is stalled
                    self.buffer[3] = self.MEM_NOOP.copy()
                    self.status = "MEM wait to load; " + self.status
                    return
                else:
                    # pass results to WB
                    self.buffer[3] = [t, response[0]]
                    self.status = "MEM loaded {} for $r{}; ".format(response[0], t) + self.status
                    self.EX()
                    return

            elif opcode in [0b101000, 0b100000]:
                # TODO: Code lb, wb
                raise ValueError("LB and WB operations not coded yet")

        # If bne, beq (condition known to be taken; otherwise, replaced by noop)
        elif current_instruction[0] in [0b000101, 0b000100]:
            opcode, t = current_instruction

            # Flush the pipeline when the branch is taken
            self.buffer = [self.IF_NOOP, self.ID_NOOP,
                           self.EX_NOOP, self.MEM_NOOP]
            self.PC = t
            self.status = "MEM branch taken to PC={}; ".format(hex(t)) + self.status
            self.EX()
            return

        # If jal
        elif current_instruction[0] == 0b000011:
            opcode, target, return_address = current_instruction

            # JAL stores $r31 = return address (PC + 4)
            self.buffer[3] = [31, return_address]
            self.EX()
            return

        # TODO: Other instructions need to be caught;
        # this else shouldn't capture all other instruction types.
        else:
            opcode, funct, reg, value = current_instruction
            self.buffer[3] = [reg, value]
            self.EX()
            return

    def WB(self):
        logging.info("WB()")

        # If syscall, note the end of program
        if self.buffer[3][0] == 0b001100:
            self.status = "WB syscall; " + self.status
            self.end_of_program = True
            self.MEM()
            return

        reg, value = self.buffer[3].copy()

        # If noop or no writeback needed, don't write back anything
        if reg == 0:
            self.status = "WB noop; "

        else:

            # Write the value to the register
            self.R[reg] = value

            # Clear reg dependency
            self.R_dependences.remove(reg)
            self.status = "WB {} to $r{}; ".format(value, reg) + self.status

            # TODO: Check if R or F register depending on instruction
            # We currently only support R register dependencies

        self.MEM()

    def set_instructions(self, instructions):
        logging.info("set_instructions()")
        """Set instructions in memory.

        Args:
            instructions (list of int): List of machine code instructions.

        # TODO: allow setting at any point in memory, not just starting at 0x0
        """
        self.memory_heirarchy[-1].data[:len(instructions)] = instructions
