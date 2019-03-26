# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:06:58 2019

@author: ayash

Next steps:

    Support pipeline off / on
    Support correct stalling for multi-cycle ALU operations
    Write unit tests 
    Plan Mar27 Demo
"""
from memory import Memory, Cache
import sys

import logging
# logging.basicConfig(level=logging.INFO)


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
    • Would cause a pipeline “bubble”
    
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
        # logging.info("__init__()")

        # Cycle count
        self.cycle = 0
        
         # Memory
        DRAM = Memory(lines=2**12, delay=100)
        L2 = Cache(lines=32, words_per_line=1, delay=2, associativity=1, next_level=DRAM, name="L2")
        L1 = Cache(lines=8, words_per_line=1, delay=1, associativity=1, next_level=L2, name="L1")
        self.memory_heirarchy = [L1, L2, DRAM]
        
        self.reset_registers()
        self.reset_memory()

    def reset_registers(self):
        # logging.info("reset_registers()")

        # Registers
        self.R = list(range(0, 32))  # Todo: replcae with self.R = [0] * 32
        self.F = [0] * 32

        # TODO: Set PC to where the first instruction is.
        self.PC = 0

        # Initialize buffer with no-ops
        self.buffer = [0, 0, 0, 0]

    def reset_memory(self):
        # logging.info("reset_memory()")
        for level in self.memory_heirarchy:
            level.reset_data()

    def step(self):
        # logging.info("step()")
        self.WB()
        self.cycle += 1
        
    def IF(self):
        # print("IF()")
        # Get the instruction to be processed and pass it along to ID stage
        # TODO: Correctly implement when we finish a program.

        # Get instruction from memory
        instruction = self.memory_heirarchy[0].read(self.PC//4) # TODO: read from address rather than line number

        # If stalled on instruction fetch from memory
        if instruction == "wait":
            # Insert noop
            self.buffer[0] = 0
            print(self.cycle, "Did not find instruction in L1:", instruction[0], "current buffer:", self.buffer)
            return

        # If noop
        elif instruction[0] == 0:
            self.buffer[0] = 0
            print(self.cycle, "Fetched a a noop:", instruction[0], "current buffer:", self.buffer)
            return

        # If a real instruction
        else:

            # Increment the program counter
            # TOOD: Should we use PC and NPC variables? Check the logic here.
            self.PC += 4
            
            self.buffer[0] = [instruction[0], self.PC]
            print(self.cycle, "Fetched instruction:", instruction[0], "current buffer:", self.buffer)
            return

    def ID(self):
        # print("ID()")
        # TODO: Add destination registers to a destination table
        # and stall if a following instruction uses a source register in the destination table

        # If noop:
        if self.buffer[0] == 0:
            self.buffer[1] = 0
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

            # TODO: use self.F instead of self.R for floating point operations
            decode_results = [opcode, self.R[s], self.R[t], d, shift, funct, PC]

        # If j-type: [opcode, target]
        elif opcode in [2, 3]:
            target = current_instruction & 0x03FFFFFF
            decode_results = [opcode, target, PC]
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
                decode_results = [opcode, self.R[s], self.R[t], immediate, PC]
  
            # If t is a destination, use value t
            # This includes: addi, andi, ori, xori, bgez, blez, bgtz, bltz, slti, lw, lb, 
            # TODO: As we add more instructions, we need to expand these lists.
            else:
                decode_results = [opcode, self.R[s], t, immediate, PC]

        # Update the buffer
        self.buffer[1] = decode_results

        # if j or jal
        if opcode in [0x2, 0x3]:
            
            # Insert a noop in the previous buffer
            self.buffer[0] = 0

            # Change the PC based on the jump address
            self.PC = (PC & 0xF0000000) | (target << 2)

        # Either way, call the IF stage.
        self.IF()

    def EX(self):
        # logging.info("EX()")

        # If noop:
        if self.buffer[1] == 0:
            self.buffer[2] = 0
            self.ID()
            return

        current_instruction = self.buffer[1].copy()

        # If R-Type
        if current_instruction[0] == 0:
            opcode, s, t, d, shift, funct, PC = current_instruction

            # If Add
            if funct == 0x20:
                execute_results = [opcode, funct, d, s+t]

            # If Sub
            elif funct == 0x22:
                execute_results = [opcode, funct, d, s-t]

            # TODO: Implement remaining r-type instructions
            else:
                raise ValueError

            # TODO: if multiple cycle ALU op, stall for one cycle.
            # If multi-cycle ALU op, add attributes for:
            # self.EX_midway_through_a_multicycle_operation
            # self.EX_cycles_remaining
            # if there are cycles remaining, decrement count and insert a noop.
            # if funct in [multicycle_ops] and self.EX_cycles_remaining != 0:
            #     self.EX_cycles_remaining = 1
            #     if self.EX_cycles_remaining == 0:
            #         # execute_results = (perform the ALU OP, and return it)
            #     else:
            #         execute_results = 0x0
            #         self.EX_cycles_remaining -= 1

        # If J-Type
        elif current_instruction[0] in [0x2, 0x3]:
            opcode, target, PC = current_instruction
            
            # TODO: Confirm PC is correct
            # If JAL
            if opcode == 0x3:
                execute_results = [opcode, target, PC + 4]

            # If J
            else:
                execute_results = [opcode, target]

        # If I-Type
        else:
            opcode, s, t, immediate, PC = current_instruction

            # If t is a source, use value self.R[t]
            # This includes: sw, sb, lw, lb
            if opcode in [0b101011, 0b101000, 0b100011, 0b100000]:
                execute_results = [opcode, t, s + (immediate << 2)]
            
            # BEQ
            elif opcode == 0b000100:
                # If branch is taken
                if s == t:
                    execute_results = [opcode, PC + (immediate << 2)]
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    execute_results = 0x0
            
            # BNEQ 
            elif opcode == 0b000101:
                # If branch is taken
                if s != t:
                    execute_results = [opcode, PC + (immediate << 2)]
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    execute_results = 0x0

            # TODO: Implement remaining r-type instructions
            else:
                raise ValueError

        self.buffer[2] = execute_results
        self.ID()

    def MEM(self):
        # logging.info("MEM()")
        # The memory stage accesses the main memory. It first attempts to get
        # the write or read from cache within 1 clock cycle (changable), 
        # and if it cannot, a stall is incurred

        # If noop:
        if self.buffer[2] == 0:
            self.buffer[3] = 0
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
                    self.buffer[3] = 0
                    return
                else:
                    self.buffer[3] = 0
                    self.EX()
                    return

            # If lw ("lw $rt offset(base)")
            elif opcode == 0b100011:

                # Write to memory
                response = self.memory_heirarchy[0].read(memory_address=s//4)
                if response == "wait":
                    # insert noop, don't call EX() since MEM is stalled
                    self.buffer[3] = 0
                    return
                else:
                    # pass results to WB
                    self.buffer[3] = [t, response[0]]
                    self.EX()
                    return

            elif opcode in [0b101000, 0b100000]:
                # TODO: Code lb, wb
                raise ValueError

        # If bne, beq (condition known to be taken; otherwise, replaced by noop)
        elif current_instruction[0] in [0b000101, 0b000100]:
            opcode, t = current_instruction

            # Flush the pipeline when the branch is taken
            self.buffer = [0, 0, 0, 0]
            self.PC = t
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
        # logging.info("WB()")
        
        if self.buffer[3] != 0:
            reg, value = self.buffer[3].copy()
            self.R[reg] = value

        self.MEM()

    def set_instructions(self, instructions):
        # logging.info("set_instructions()")
        """Set instructions in memory.
        
        Args:
            instructions (list of int): List of machine code instructions.

        # TODO: allow setting at any point in memory, not just starting at 0x0
        """
        self.memory_heirarchy[-1].data[:len(instructions)] = instructions