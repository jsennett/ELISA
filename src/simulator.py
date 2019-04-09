"""

Josh Sennett
Yash Adhikari
CS 535

Simulator

"""
from memory import Memory, Cache
from utils import f_to_b, b_to_f

import logging
logging.basicConfig(level=logging.INFO)


class Simulator:
    """
    Notes below from source:
    https://www.ece.ucsb.edu/~strukov/ece154aFall2013/viewgraphs/pipelinedMIPS.pdf
    https://en.wikibooks.org/wiki/MIPS_Assembly/Instruction_Formats

    TODO:
        Implement multi-operation ALU and FP operations. Look up # cycles.
        Catch condition codes after ALU operations, e.g. overflow
    """

    def __init__(self):
        """Initialize a Simulator.

        Define configuration options and NOOP formats for convenient use later
        Then, set changing attributes using the reset()

        """
        logging.info("__init__()")

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

        # Status
        self.status = ""

        # Enable or disable pipeline - passed value from GUI
        self.pipeline_enabled = True

        # flag to only load one instruction at a time (No pipeline)
        # logic only used when pipeline turned off (runs in the background)
        self.instruction_processing = False
        self.instruction_stage = 0

        # EX stage may have instructions that need multiple cycles to complete
        # which must be tracked
        self.EX_cycles_remaining = 0
        self.EX_multiple_cycle_instruction = False

        # (Re)set values of registers and memory
        self.reset()


    def reset(self):
        logging.info("reset()")

        # Whether the program is terminated
        self.end_of_program = False

        # Registers
        self.R = [0] * 32
        self.F = [0] * 32
        self.PC = 0
        self.HI = 0
        self.LO = 0
        self.CC = 0

        # Cycle count
        self.cycle = 0

        # Create a set of destination registers that need to be updated
        # TODO: see if hi/lo/pc/control registers need to be tracked
        self.R_dependences = set()  # Integer registers
        self.F_dependences = set()  # FP registers

        # Initialize buffer with no-ops
        self.buffer = [self.IF_NOOP, self.ID_NOOP, self.EX_NOOP, self.MEM_NOOP]

        # Reset memory values
        for level in self.memory_heirarchy:
            level.reset_data()

        # Status message; initialized empty
        self.status = ""

    def step(self):
        logging.info("step()")
        self.status = ""
        self.WB()
        self.cycle += 1

        logging.info("Cycle {} - {}".format(self.cycle, self.status))
        logging.info("Current buffer contents:" + str(self.buffer))

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

        # if (pipelining is turned on) or (pipelining is turned off but the next
        # instruction is ready to be loaded / no instruction is processing)
        if self.instruction_stage == 5:
            self.instruction_stage = 0

        #if self.pipeline_enabled or not(self.instruction_processing):
        if self.pipeline_enabled or self.instruction_stage == 0:

            # Get instruction from memory
            instruction = self.memory_heirarchy[0].read(self.PC) # TODO: read from address rather than line number

            # If stalled on instruction fetch from memory
            if instruction == "wait":
                # Insert noop
                self.buffer[0] = [0, 0]
                self.status = "IF wait to load inst; " + self.status

                # if waiting for instruction set parameter to 0
                self.instruction_stage = 0
                return


            # Increment the program counter
            # TOOD: Should we use PC and NPC variables? Check the logic here.
            self.PC += 4

            self.buffer[0] = [instruction[0], self.PC]
            self.status = "IF fetched instruction; " + self.status

            # Change status to currently processing instruction
            self.instruction_processing = True
            self.instruction_stage += 1

            return

        # else: pass on noops (do not update PC)
        else:
            self.buffer[0] = [0, 0]

            # knowing that IF stage is only called when there are no stalls
            # from other stages (in case IF stalls, set parameter to 0)
            self.instruction_stage += 1
            self.status = "IF stalled; " + self.status


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

            # Handle jr and jalr first which are only dependent on register s
            if funct in [0b001000, 0b001001]:
                if (s in self.R_dependences):
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    target = self.R[s]
                    decode_results = [opcode, target, self.R[t], d, shift, funct, PC]
                    self.status = "ID J-type decoded; " + self.status

                    # add dependency for jalr
                    if funct == 0b001001:
                        self.R_dependences.add(d)

            # Handle mflo / mfhi dependences
            elif funct in [0b010010, 0b010000]:

                # Add destination d to the destination table
                self.R_dependences.add(d)

                # Check if sources hi/lo are in the destination table
                if 64 in self.R_dependences:
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    val = self.HI if funct == 0b010000 else self.LO
                    decode_results = [opcode, val, 0, d, 0, funct, PC]
            # R: [opcode, s, t, d, shift, funct, PC]
            else:
                # If data dependency then stall - pass a noop and don't call IF
                # r0 cannot be changed, so it should not cause a stall
                if s in self.R_dependences or t in self.R_dependences:

                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return

                else:
                    # TODO: use self.F instead of self.R for floating point operations
                    decode_results = [opcode, self.R[s], self.R[t], d, shift, funct, PC]
                    if current_instruction == 0:
                        self.status = "ID NOOP; " + self.status
                    else:
                        self.status = "ID R-type decoded; " + self.status

                    # Update dependency table. Note that a destination of r0
                    # does not cause a dependency since it has a fixed value zero

                    if d != 0:
                        self.R_dependences.add(d)

                    # Also, we must add lo and hi registers to dependency
                    # if instruction requiring their use is called
                    if funct in [0b011000, 0b011010]:
                        self.R_dependences.add(64) # represents both lo and hi

        # If j-type - instruction j
        elif opcode == 0b000010:
            target = current_instruction & 0x03FFFFFF
            decode_results = self.ID_NOOP
            self.status = "ID J-type decoded; " + self.status

        # If j-type - instruction jal
        elif opcode == 0b000011:
            target = current_instruction & 0x03FFFFFF
            decode_results = [opcode, target, PC]
            self.status = "ID J-type decoded; " + self.status

            # Add dependency on regiester 31 for JAl instruction
            self.R_dependences.add(31)


        # If floating point instruction (does not include  l.s, s.s)
        # may need to remove the (current_instruction & 0x3E00000) >> 21 for more instructions
        elif opcode == 0b010001 and (current_instruction & 0x3E00000) >> 21 == 0b010000:
            special = (current_instruction & 0x03E00000) >> 21
            t = (current_instruction & 0x001F0000) >> 16
            s = (current_instruction & 0x0000F800) >> 11
            d = (current_instruction & 0x000007C0) >> 6
            funct = (current_instruction & 0x3F)


            # If data dependency then stall - pass a noop and don't call IF
            if s in self.F_dependences or t in self.F_dependences:

                self.status = "ID data dependency; " + self.status
                self.buffer[1] = self.ID_NOOP.copy()
                return

            else:

                self.status = "ID FP Instruction; " + self.status
                # if control flow instructions c.eq.s, c.le.s, c.lt.s
                if (current_instruction & 0x0000000F) in [0x2, 0xe, 0xc]:
                    # comparing fp instructions have a slightly different format
                    # 0x11, 0x10, ft, fs, cc, 0, FC, 0xe: taking [6,5,5,5,3,2,24] bits respectively
                    decode_results = [opcode, self.F[s], self.F[t], d+32, special, current_instruction & 0x0000000F, PC]

                else:
                    # add 32 to the register # d in order to let WB stage know
                    # that it needs to write to the floating point regiesters
                    decode_results = [opcode, self.F[s], self.F[t], d+32, special, funct, PC]

                    # Update dependency table for floating point registers
                    self.F_dependences.add(d)

        # if bc1t bc1f fp instruction in a different format
        # 0x11 8 cc 0 Offset: taking [6 5 3 2 16] bits respectively
        elif opcode == 0b010001 and (current_instruction & 0x03E00000) >> 21 == 0x8:
            special = (current_instruction & 0x03E00000) >> 21
            immediate = current_instruction & 0x000FFFF
            funct = (current_instruction & 0x00030000) >> 16
            cc = (current_instruction & 0x00070000) >> 18

            # Sign extension
            if (immediate >> 15 == 1):
                immediate = -1*(immediate ^ 0xFFFF)-1

            # pass '0' values as fillers, handled properly in the EX stage
            decode_results = [opcode, 0, cc, immediate, special, funct, PC]

        # if s.s l.s - needs to be different from I-format b/c s is a
        # t is a floating point register
        elif opcode in [0b111001, 0b110001] :
            s = (current_instruction & 0x03E00000) >> 21
            t = (current_instruction & 0x001F0000) >> 16
            immediate = current_instruction & 0x0000FFFF

            # Sign extension
            if (immediate >> 15 == 1):
                immediate = -1*(immediate ^ 0xFFFF)-1

            # If t is a source, use value self.R[t]: s.s**
            if opcode == 0b111001 :

                # If data dependency then stall - pass a noop
                if s in self.R_dependences or t in self.F_dependences:
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    self.status = "ID I-type decoded; " + self.status
                    decode_results = [opcode, self.R[s], self.F[t], immediate, PC]

            # If t is a destination, use value t: l.s**
            else:
                # If data dependency then stall - pass a noop
                if s in self.R_dependences:
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    self.status = "ID I-type decoded; " + self.status
                    decode_results = [opcode, self.R[s], t+32, immediate, PC]

                    if opcode not in [0b000001, 0b000110, 0b000111, 0b000001]:
                        self.F_dependences.add(t)

        # If i-type: [opcode, s, t, immediate]
        else:
            s = (current_instruction & 0x03E00000) >> 21
            t = (current_instruction & 0x001F0000) >> 16
            immediate = current_instruction & 0x0000FFFF

            # Sign extension; note this means ALU operations will
            # (purposefully) overflow
            if (immediate >> 15 == 1):
                immediate = (immediate | 0xFFFF0000)

            # If t is a source, use value self.R[t]
            # This includes: beq, bne, sw, sb, s.s**
            if opcode in [0b000100, 0b000101, 0b101011, 0b101000, 0b111001]:

                # If data dependency then stall - pass a noop
                if s in self.R_dependences or t in self.R_dependences:
                    self.status = "ID data dependency; " + self.status
                    self.buffer[1] = self.ID_NOOP.copy()
                    return
                else:
                    self.status = "ID I-type decoded; " + self.status
                    decode_results = [opcode, self.R[s], self.R[t], immediate, PC]

            # If t is a destination, use value t
            # This includes: addi, andi, ori, xori, slti, lw, lb, bgez, blez, bgtz, bltz, l.s**
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

                    if opcode not in [0b000001, 0b000110, 0b000111, 0b000001]:
                        self.R_dependences.add(t)

        # Update the buffer
        self.buffer[1] = decode_results

        # TODO: Shift this logic into the J-Type section above ** may not want
        # to do that since jr and jalr are not j type
        # if j, jal, jr, or jalr
        if opcode in [0x2, 0x3]:
            # Insert a noop in the previous buffer
            self.buffer[0] = [0, PC]
            # Change the PC based on the jump address
            self.PC = (PC & 0xF0000000) | (target << 2)
        if (opcode == 0 and (current_instruction & 0x3F) in [0b001000, 0b001001]):
            # Insert a noop in the previous buffer
            self.buffer[0] = [0, PC]
            # Change the PC based on the jump address
            self.PC = target

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
        logging.info("buffer 2: {}".format(self.buffer[2]))
        if self.buffer[1][0] == 0b001100 and len(self.buffer[1]) == 2:
            self.buffer[2] = self.buffer[1].copy()
            self.status = "EX syscall; " + self.status
            self.ID()
            return

        current_instruction = self.buffer[1].copy()

        # If R-Type
        if current_instruction[0] == 0:
            opcode, s, t, d, shift, funct, PC = current_instruction

            # If Add
            if funct == 0b100000:
                execute_results = [opcode, funct, d, s+t]
                self.status = "EX add; " + self.status

            # If Sub
            elif funct == 0b100010:
                execute_results = [opcode, funct, d, (s-t) & 0xFFFFFFFF]
                self.status = "EX sub; " + self.status

            # If bitwise and
            elif funct == 0b100100:
                execute_results = [opcode, funct, d, (s&t) & 0xFFFFFFFF]
                self.status = "EX and; " + self.status

            # If bitwise or
            elif funct == 0b100101:
                execute_results = [opcode, funct, d, (s|t) & 0xFFFFFFFF]
                self.status = "EX or; " + self.status

            # If bitwise nor
            elif funct == 0b100111:
                execute_results = [opcode, funct, d, ((~s)&(~t)) & 0xFFFFFFFF]
                self.status = "EX nor; " + self.status

            # If xor
            elif funct == 0b100110:
                execute_results = [opcode, funct, d, (s^t) & 0xFFFFFFFF]
                self.status = "EX xor; " + self.status

            # If slt
            elif funct == 0b101010:
                if s < t:
                    execute_results = [opcode, funct, d, 1]
                else:
                    execute_results = self.EX_NOOP.copy()

                self.status = "EX slt; " + self.status

            # If mflo or mfhi
            elif funct in [0b010010, 0b010000]:
                execute_results = [opcode, funct, d, s]
                self.status = "EX mfhi/lo val {} to {}; ".format(s, d) + self.status

            # For multi-cycle ALU operations, if there are cycles remaining,
            # decrement the count of cycles and insert a noop.
            elif funct in [0b011000, 0b011010]:

                # If multi-cycle operation but no more cycles remaining
                if self.EX_cycles_remaining == 0 and self.EX_multiple_cycle_instruction:

                    # mulitply
                    if funct == 0b011000:
                        value = s*t
                        execute_results = [opcode, funct, 64, [value >> 32, value & 0xFFFFFFFF]]
                        self.status = "EX mult; " + self.status
                    # divide
                    elif funct == 0b011010:
                        execute_results = [opcode, funct, 64, [s%t, s//t]]
                        self.status = "EX div {}/{}; ".format(s, t) + self.status

                    self.EX_multiple_cycle_instruction = False

                # If cycles remaining or instruction not identified as
                # multicycle yet
                else:

                    # if instruction is not knon to be multiple cycles, make it
                    # known to be and increase cycles remaining
                    if not(self.EX_multiple_cycle_instruction):
                        self.EX_multiple_cycle_instruction = True

                        # Assume all multicycle ops delay a single cycle
                        self.EX_cycles_remaining = 1

                    # Decrement cycle
                    self.EX_cycles_remaining -= 1

                    # Insert noop
                    self.buffer[2] = self.EX_NOOP.copy()
                    self.status = "EX stall for multicycle ALU; " + self.status
                    return

            # if jr which is also R-type pass a noop as nothing is left to do
            elif funct == 0b001000:
                execute_results = self.EX_NOOP.copy()

            # if jalr which is also R-type
            elif funct == 0b001001:
                execute_results = [opcode, funct, d, PC]

            # If sll; note that this also includes noops
            elif funct == 0:
                execute_results = [opcode, funct, d, t << shift]
                if d == 0 and t == 0 and shift == 0:

                    self.status = "EX noop; " + self.status
                else:
                     self.status = "EX sll; " + self.status

            # If srl
            elif funct == 0b000010:
                execute_results = [opcode, funct, d, t >> shift]
                self.status = "EX srl; " + self.status

            # If sra
            elif funct == 0b000011:
                sign = t >> 31
                val = t >> shift
                for i in range(shift):
                    val |= (sign << (31 - i))
                execute_results = [opcode, funct, d, val]
                self.status = "EX sra; " + self.status

             # TODO: Implement remaining r-type instructions
            else:
                raise ValueError('Unknown funct {:05b} for R-Type with \
                                 opcode: {:06b}'.format(funct, opcode))

        # If J-Type (only JAL)
        elif current_instruction[0] == 0b000011:
            opcode, target, PC = current_instruction

            # TODO: Confirm PC is correct
            execute_results = [opcode, target, PC]

        # If floating point instructions (does not include control flow and l.s, s.s)
        # can be addressed in the ID stage
        elif current_instruction[0] == 0b010001:
            opcode, s, t, d, special, funct, PC = current_instruction

            # if bc1t or bc1f
            if special == 0x8:
                # properly represent values, currently ccc in insttruction not used
                # value in s is junk, t = cc from instruction, d = immediate
                condition_code = t
                immediate = d

                # if bc1f
                if funct == 0:
                    # If branch is taken
                    if self.CC == False:
                        execute_results = [opcode, special, PC - 4 + (immediate << 2)]
                        self.status = "EX bc1f, taken; " + self.status
                    # If branch is not taken push a noop (nothing occurs during MEM
                    # and WB stage)
                    else:
                        self.status = "EX bc1f, not taken; " + self.status
                        execute_results = self.EX_NOOP.copy()

                # elif bc1t
                elif funct == 1:
                    # If branch is taken
                    if self.CC == True:
                        execute_results = [opcode, special, PC - 4 + (immediate << 2)]
                        self.status = "EX bc1t, taken; " + self.status
                    # If branch is not taken push a noop (nothing occurs during MEM
                    # and WB stage)
                    else:
                        self.status = "EX bc1t, not taken; " + self.status
                        execute_results = self.EX_NOOP.copy()

                # else error
                else:
                    raise ValueError("Unknown FP instruction: {}".format(funct))

            # else other fp instructions other than l.s and s.s
            else:

                # add.s
                if funct == 0b000000:
                    execute_results = [opcode, funct, d, f_to_b(b_to_f(s) + b_to_f(t))]
                    self.status = "EX add.s; " + self.status


                # sub.s
                elif funct == 0b000001:
                    execute_results = [opcode, funct, d, f_to_b(b_to_f(s) - b_to_f(t))]
                    self.status = "EX add.s; " + self.status


                # c.eq.s
                elif funct == 0x2:
                    if b_to_f(s) == b_to_f(t):
                        self.CC = True
                    else:
                        self.CC = False
                    execute_results = self.EX_NOOP.copy()

                # c.le.s
                elif funct == 0xe:
                    if b_to_f(s) <= b_to_f(t):
                        self.CC = True
                    else:
                        self.CC = False
                    execute_results = self.EX_NOOP.copy()

                # c.lt.s
                elif funct == 0xc:
                    if b_to_f(s) < b_to_f(t):
                        self.CC = True
                    else:
                        self.CC = False
                    execute_results = self.EX_NOOP.copy()

                # currently mul.s is in big conflict with c.eq.s
                # mul.s, div.s
                elif funct in [0b000010, 0b000011]:
                    pass

        # If I-Type
        # includes floating point l.s and s.s
        else:
            opcode, s, t, immediate, PC = current_instruction
            i_sign = (immediate >> 31) & 0b1

            # If t is a source, use value self.R[t]
            # This includes: sw, sb, lw, lb, s.s, l.s
            if opcode in [0b101011, 0b101000, 0b100011, 0b100000, 0b111001, 0b110001]:
                execute_results = [opcode, t, s + (immediate << 2)]
                self.status = "EX load or store; " + self.status

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
            # BGEZ
            elif opcode == 0b000001 and t == 1:
                # If branch is taken
                if s >= 0:
                    execute_results = [opcode, PC - 4 + (immediate << 2)]
                    self.status = "EX bgez, taken; " + self.status
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    self.status = "EX bgez, not taken; " + self.status
                    execute_results = self.EX_NOOP.copy()
            # BLEZ
            elif opcode == 0b000110:
                # If branch is taken
                if s <= 0:
                    execute_results = [opcode, PC - 4 + (immediate << 2)]
                    self.status = "EX blez, taken; " + self.status
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    self.status = "EX blez, not taken; " + self.status
                    execute_results = self.EX_NOOP.copy()
            # BGTZ
            elif opcode == 0b000111:
                # If branch is taken
                if s > 0:
                    execute_results = [opcode, PC - 4 + (immediate << 2)]
                    self.status = "EX bgtz, taken; " + self.status
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    self.status = "EX bgtz, not taken; " + self.status
                    execute_results = self.EX_NOOP.copy()
            # BLTZ
            elif opcode == 0b000001 and t == 0:
                # If branch is taken
                if s < 0:
                    execute_results = [opcode, PC - 4 + (immediate << 2)]
                    self.status = "EX bltz, taken; " + self.status
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    self.status = "EX bltz, not taken; " + self.status
                    execute_results = self.EX_NOOP.copy()
            # addi
            elif opcode == 0b001000:
                execute_results = [opcode, 0, t, (s + immediate) & 0xFFFFFFFF]
                self.status = "EX addi; " + self.status

            # If slti
            elif opcode == 0b001010:
                s_sign = (s >> 31) & 1
                print('s: {}, immediate: {}'.format(s, immediate))
                print('s_sign: {}, i_sign: {}'.format(s_sign, i_sign))

                # If s < immediate, set = 1
                if (((s_sign == i_sign) and (s < immediate))
                    or ((s_sign != i_sign) and (s > immediate))):
                    execute_results = [opcode, 0, t, 1]

                # If s >= immediate, set = 0
                else:
                    execute_results = [opcode, 0, t, 0]
                self.status = "EX slti; " + self.status

            # andi
            elif opcode == 0b001100:
                execute_results = [opcode, 0, t, s & immediate]
                self.status = "EX andi; " + self.status

            # ori
            elif opcode == 0b001101:
                execute_results = [opcode, 0, t, s | immediate]
                self.status = "EX ori; " + self.status

            # xori
            elif opcode == 0b001110:
                execute_results = [opcode, 0, t, s ^ immediate]
                self.status = "EX xori; " + self.status

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
            writeback: [reg, value]
        """
        logging.info("MEM()")
        # The memory stage accesses the main memory. It first attempts to get
        # the write or read from cache within 1 clock cycle (changable),
        # and if it cannot, a stall is incurred

        # If syscall
        if self.buffer[2][0] == 0b001100 and len(self.buffer[2]) == 2:
            self.buffer[3] = -1   # We need a distinct syscall code to differentiate from a WB
            self.status = "MEM syscall; " + self.status
            self.EX()
            return

        current_instruction = self.buffer[2].copy()

        # If lw, lb, l.s, sw, sb, s.s
        if current_instruction[0] in [0b101011, 0b101000, 0b110001, 0b100011, 0b100000, 0b111001]:
            opcode, t, s = current_instruction

            # If s.s, sw or sb ("sw $rt offset(base)")
            if opcode in [0b111001, 0b101011, 0b101000]:

                # word or byte?
                only_byte = True if opcode == 0b101000 else False
                mnemonic = "sw" if opcode == 0b100011 else "sb" if opcode == 0b101000 else "s.s"

                # Write to memory
                response = self.memory_heirarchy[0].write(memory_address=s, value=t, only_byte=only_byte)
                if response == "wait":
                    # insert noop, don't call EX() since MEM is stalled
                    self.buffer[3] = self.MEM_NOOP
                    self.status = "MEM wait to {}; ".format(mnemonic) + self.status
                    return
                else:
                    self.buffer[3] = self.MEM_NOOP
                    self.status = "MEM {} successful; ".format(mnemonic) + self.status
                    self.EX()
                    return

            # If l.s, lw or lb ("lw $rt offset(base)")
            elif opcode in [0b110001, 0b100011, 0b100000]:

                # word or byte?
                only_byte = True if opcode == 0b100000 else False
                mnemonic = "lw" if opcode == 0b100011 else "lb" if opcode == 0b100000 else "l.s"

                # Write to memory
                response = self.memory_heirarchy[0].read(memory_address=s, only_byte=only_byte)
                if response == "wait":
                    # insert noop, don't call EX() since MEM is stalled
                    self.buffer[3] = self.MEM_NOOP.copy()
                    self.status = "MEM wait to {}; ".format(mnemonic) + self.status
                    return
                else:
                    # pass results to WB
                    self.buffer[3] = [t, response[0]]
                    self.status = "MEM {} successful; ".format(mnemonic) + self.status
                    self.EX()
                    return

        # If bne, beq, bgez, blez, bgtz, bltz (condition known to be taken;
        # otherwise, the buffer would have been replaced by a noop)
        elif current_instruction[0] in [0b000101, 0b000100, 0b000001,
                                        0b000110, 0b000111, 0b000001]:
            opcode, t = current_instruction

            # Flush the pipeline when the branch is taken
            self.buffer = [self.IF_NOOP, self.ID_NOOP,
                           self.EX_NOOP, self.MEM_NOOP]

            # Update the PC with the new value
            self.PC = t
            self.status = "MEM branch taken to PC={}; ".format(hex(t)) + self.status
            self.EX()
            return

        # If jal
        elif current_instruction[0] == 0b000011: #or (current_instruction[0] == 0 and (current_instruction[0] & 0x3F) == 0b001001):
            opcode, target, return_address = current_instruction
            # JAL stores $r31 = return address (PC + 4)
            self.buffer[3] = [31, return_address]
            self.EX()
            return

        # If j - do not need WB stage - pass a noop
        elif current_instruction[0] == 0b000010:
            self.buffer[3] = self.MEM_NOOP
            self.EX()
            return

        # if bc1t or bc1f  [when branch is taken]
        elif current_instruction[0] == 0b010001 and current_instruction[1] == 0x8 and len(current_instruction) == 3:
            opcode, special, t = current_instruction

            # Flush the pipeline when the branch is taken
            self.buffer = [self.IF_NOOP, self.ID_NOOP,
                           self.EX_NOOP, self.MEM_NOOP]

            # Update the PC with the new value
            self.PC = t
            self.status = "MEM branch taken to PC={}; ".format(hex(t)) + self.status
            self.EX()
            return


        # TODO: Other instructions need to be caught;
        # this else shouldn't capture all other instruction types.
        # does include jalr
        else:
            opcode, funct, reg, value = current_instruction

            self.buffer[3] = [reg, value]
            self.EX()
            return

    def WB(self):
        logging.info("WB()")

        # If syscall, note the end of program
        if self.buffer[3] == -1:
            self.status = "WB syscall; " + self.status
            self.end_of_program = True
            self.MEM()
            return

        reg, value = self.buffer[3].copy()

        # If noop or no writeback needed, don't write back anything
        if reg == 0:
            self.status = "WB noop; "

        elif reg >= 32 and reg <= 63:
            # Write the value to the register
            self.F[reg-32] = value

            # Clear reg dependency
            self.F_dependences.remove(reg-32)
            self.status = "WB {} to $f{}; ".format(value, reg) + self.status

        # if reg parameter is set to 64 indicating we need to set hi and lo reg
        elif reg == 64:
            # Write the value to the register
            self.HI = value[0]
            self.LO = value[1]

            # Clear reg dependency
            self.R_dependences.remove(reg)
            self.status = "WB {} to $r{}; ".format(value, 'hi, lo') + self.status
        else:

            # Write the value to the register
            self.R[reg] = value

            # Clear reg dependency
            self.R_dependences.remove(reg)
            self.status = "WB {} to $r{}; ".format(value, reg) + self.status

            # TODO: Check if R or F register depending on instruction
            # We currently only support R register dependencies

        self.MEM()

    def set_instructions(self, instructions, data_section=None):
        logging.info("set_instructions()")
        """Set instructions in memory.

        Args:
            instructions (list of int): List of machine code instructions.

        # TODO: allow setting at any point in memory, not just starting at 0x0
        """
        self.memory_heirarchy[-1].data[:len(instructions)] = instructions
        if data_section is not None:
            for idx in data_section:
                self.memory_heirarchy[-1].data[idx] = data_section[idx]

