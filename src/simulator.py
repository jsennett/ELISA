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

        # Cycle count
        self.cycle = 0
        
         # Memory
        DRAM = Memory(lines=2**12, delay=100)
        L1 = Cache(lines=8, words_per_line=1, delay=1, associativity=1, next_level=DRAM, name="L1")
        L2 = Cache(lines=32, words_per_line=1, delay=1, associativity=1, next_level=L1, name="L2")
        self.memory_heirarchy = [L1, L2, DRAM]
        
        self.reset_registers()
        self.reset_memory()

    def reset_registers(self):

        # Registers
        self.R = list(range(100, 132))  # Todo: replcae with self.R = [0] * 32
        self.F = [0] * 32

        # TODO: Set PC to where the first instruction is.
        self.PC = 0

        # Initialize buffer with no-ops
        self.buffer = [0, 0, 0, 0]

    def reset_memory(self):
        for level in self.memory_heirarchy:
            level.reset_data()

    def step(self):
        self.WB()
        
    def IF(self):
        # Get the instruction to be processed and pass it along to ID stage
        # TODO: Correctly implement when we finish a program.

        # Get instruction from memory
        instruction = self.memory_heirarchy[0].read(self.PC)
        if instruction == "wait":
            # Insert noop
            self.buffer[0] = 0x0
            return
        
        self.NPC = self.PC + 4
        
        # TODO: Check logic
        self.PC = self.NPC
        
        self.buffer[0] = instruction
        print("IF: Fetched instruction:", instruction)

    def ID(self):

        current_instruction = self.buffer[0]

        # If noop:
        if current_instruction == 0:
            self.buffer[1] = [0]
            self.IF()
            return

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
            decode_results = [opcode, self.R[s], self.R[t], d, shift, funct]

        # If j-type: [opcode, target]
        elif opcode in [2, 3]:
            target = current_instruction & 0x03FFFFFF
            decode_results = [opcode, target]
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
                decode_results = [opcode, self.R[s], self.R[t], immediate]
  
            # If t is a destination, use value t
            # This includes: addi, andi, ori, xori, bgez, blez, bgtz, bltz, slti, lw, lb, 
            # TODO: As we add more instructions, we need to expand these lists.
            else:
                decode_results = [opcode, self.R[s], t, immediate]

        self.buffer[1] = decode_results

        # if jump: 
        if opcode in [0x2, 0x3]:
            self.buffer[0] = 0x0
        # if not jump, call fetch, which will update buffer[0]:
        else:
            self.IF()

    def EX(self):
        current_instruction = self.buffer[1].copy()

        # If noop:
        if len(current_instruction) == 1 and current_instruction[0] == 0:
            self.buffer[2] = 0
            self.ID()
            return

        # If R-Type
        if current_instruction[0] == 0:
            opcode, s, t, d, shift, funct = current_instruction

            # If Add
            if opcode == 0x20:
                execute_results = [opcode, funct, d, s+t]
            # If Sub
            elif opcode == 0x22:
                execute_results = [opcode, funct, d, s-t]

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
            opcode, target = current_instruction
            
            # TODO: Confirm PC is correct
            # If JAL
            if opcode == 0x3:
                execute_results = [opcode, self.PC + 8, target]
            else:
            # If J
                execute_results = [opcode, target]

        # If I-Type
        else:
            opcode, s, t, immediate = current_instruction

            
            # If t is a source, use value self.R[t]
            # This includes: sw, sb, lw, lb
            if opcode in [0b101011, 0b101000, 0b100011, 0b100000]:
                execute_results = [opcode, t, s + (immediate << 2)]
            
            # BEQ
            elif opcode == 0b000100:
                # If branch is taken
                if s == t:
                    execute_results = [opcode, self.PC + (immediate << 2)]
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    execute_results = [0x0]
            
            # BNEQ 
            elif opcode == 0b000101:
                # If branch is taken
                if s != t:
                    execute_results = [opcode, self.PC + (immediate << 2)]
                # If branch is not taken push a noop (nothing occurs during MEM
                # and WB stage)
                else:
                    execute_results = [0x0]
            
                
        # TODO: if multiple cycle ALU op, stall for one cycle.
        self.buffer[2] = execute_results

    def MEM(self):
        # The memory stage accesses the main memory. It first attempts to get
        # the write or read from cache within 1 clock cycle (changable), 
        # and if it cannot, a stall is incurred
        current_instruction = self.buffer[2].copy()

        # If noop:
        if len(current_instruction) == 1 and current_instruction[0] == 0:
            self.buffer[2] = 0
            self.EX()
            return
        
        # If I-Type
        if not(current_instruction[0] in [0, 0x2, 0x3]):
        # If the instruction is a read from memory to store in register               
        
        # If the instruction is a write to memory address

        # If instruction is a branch that is taken, set the correct the PC  
        # in the buffer and flush the IF ID and EX stages with noops
        
        # else push noop
        
    # # def EX(self):
    #     # The execute stage calculates relevant values using the ALU. It either
    #     # calculates the operation or an address for loading, storing, or 
    #     # jumping
        
    #     # Pass along values
    #     self.EX_MEM_Opcode[0] = self.ID_EX_Opcode[1]
        
    #     # R-format
    #     # If ADD
    #     if (self.ID_EX_Function[1] == 0x20):
    #         logging.info("[3] \t EX: ADD")
    #         self.EX_MEM_Zero[0] = 0xf
    #         self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + self.ID_EX_ReadReg2Value[1]
    #         self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
    #         self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_15_11[1]

    #         self.EX_MEM_MemRead[0] = 0
    #         self.EX_MEM_MemWrite[0] = 0
    #         self.EX_MEM_MemToReg[0] = 0
    #         self.EX_MEM_RegWrite[0] = 1
            
    #     # If SUB
    #     elif (self.ID_EX_Function[1] == 0x22):
    #         logging.info("[3] \t EX: SUB")
    #         self.EX_MEM_Zero[0] = 0xf
    #         self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] - (self.ID_EX_ReadReg2Value[1])
    #         self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
    #         self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_15_11[1]

    #         self.EX_MEM_MemRead[0] = 0
    #         self.EX_MEM_MemWrite[0] = 0
    #         self.EX_MEM_MemToReg[0] = 0
    #         self.EX_MEM_RegWrite[0] = 1
            
    #     # I format
    #     else:
    #         # If LB
    #         if(self.ID_EX_Opcode[1] == 0x20 and self.ID_EX_MemWrite[1] == 0 and self.ID_EX_MemToReg[1] == 1):
    #             logging.info("[3] \t EX: LB")
    #             self.EX_MEM_Zero[0] = 0xf
    #             self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
    #             self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
    #             self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_20_16[1]
    
    #             self.EX_MEM_MemRead[0] = 1
    #             self.EX_MEM_MemWrite[0] = 0
    #             self.EX_MEM_MemToReg[0] = 1
    #             self.EX_MEM_RegWrite[0] = 1
            
    #         # If SB
    #         elif (self.ID_EX_Opcode[1] == 0x28 and self.ID_EX_MemWrite[1] == 1):
    #             logging.info("[3] \t EX: SB")
    #             self.EX_MEM_Zero[0] = 0xf;
    #             self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
    #             self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
    #             self.EX_MEM_WriteRegNum[0] = 0
    
    #             self.EX_MEM_MemRead[0] = 0
    #             self.EX_MEM_MemWrite[0] = 1
    #             self.EX_MEM_MemToReg[0] = 0
    #             self.EX_MEM_RegWrite[0] = 0
            
    #         # If LW
    #         elif(self.ID_EX_Opcode[1] == 0x23 and self.ID_EX_MemWrite[1] == 0 and self.ID_EX_MemToReg[1] == 1):
    #             logging.info("[3] \t EX: LW")
    #             self.EX_MEM_Zero[0] = 0xf
    #             self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
    #             self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
    #             self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_20_16[1]
    
    #             self.EX_MEM_MemRead[0] = 1
    #             self.EX_MEM_MemWrite[0] = 0
    #             self.EX_MEM_MemToReg[0] = 1
    #             self.EX_MEM_RegWrite[0] = 1
            
    #         # If SW
    #         elif (self.ID_EX_Opcode[1] == 0x2B and self.ID_EX_MemWrite[1] == 1):
    #             logging.info("[3] \t EX: SW")
    #             self.EX_MEM_Zero[0] = 0xf;
    #             self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
    #             self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
    #             self.EX_MEM_WriteRegNum[0] = 0
    
    #             self.EX_MEM_MemRead[0] = 0
    #             self.EX_MEM_MemWrite[0] = 1
    #             self.EX_MEM_MemToReg[0] = 0
    #             self.EX_MEM_RegWrite[0] = 0
                
    #         else:
    #             # If J or JAL
    #             if (self.ID_EX_Opcode[1] == 0x02 or self.ID_EX_Opcode[1] == 0x03):
    #                 logging.info("[3] \t EX: J or JAL")

    #                 # Calculate the address and change PC and instruction
    #                 self.IF_ID_PC[0] = (self.IF_ID_PC[0] & 0xF0000000) ^ (self.ID_EX_Target[1]<<2)

    #                 # If we finish the program:
    #                 # TODO: Correctly implement when we finish a program.
    #                 instruction_idx = self.IF_ID_PC[0]//4
    #                 if instruction_idx >= len(self.instructions):
    #                     logging.info("Program finished.")
    #                     return

    #                 self.IF_ID_Inst[0] = self.instructions[self.IF_ID_PC[0]//4]
    #                 self.IF_ID_PC[0] += 4
    #                 self.PC = self.IF_ID_PC[0]
                    
    #                 # Todo: More work needed for Jump and link (JAL): set return register to the link address
                    
    #             # If NOP
    #             else:
    #                 logging.info("[3] \t EX: NOP")
    #                 self.EX_MEM_MemRead[0] = 0
    #                 self.EX_MEM_MemWrite[0] = 0
    #                 self.EX_MEM_MemToReg[0] = 0
    #                 self.EX_MEM_RegWrite[0] = 0
                    
    #                 self.EX_MEM_Zero[0] = 0
    #                 self.EX_MEM_ALUResult[0] = 0
    #                 self.EX_MEM_SWValue[0] = 0
    #                 self.EX_MEM_WriteRegNum[0] = 0
            
            
    # def MEM(self):
    #     # The Ememory stage accesses the main memory. It first attempts to get
    #     # the write or read from cache within 1 clock cycle (changable), 
    #     # and if it cannot, a stall is incurred
        
    #     # Transfer control bits from the execute stage into the memory stage.
    #     self.MEM_WB_ALUResult[0] = self.EX_MEM_ALUResult[1]
    #     self.MEM_WB_WriteRegNum[0] = self.EX_MEM_WriteRegNum[1]
    #     self.MEM_WB_MemToReg[0] = self.EX_MEM_MemToReg[1]
    #     self.MEM_WB_RegWrite[0] = self.EX_MEM_RegWrite[1]
        
    #     # If the instruction is a read or write from memory
    #     if(self.EX_MEM_MemRead[1] == 1 or self.EX_MEM_MemWrite[1] == 1):
            
    #         # If load (if you are reading from memory and if you are writing to register)
    #         if (self.EX_MEM_MemRead[1] == 1 and self.EX_MEM_RegWrite[1] == 1):
                
    #             # If LW
    #             if(self.EX_MEM_Opcode[1] == 0x23):
    #                 logging.info("[4] \tMEM: LW")

    #                 # stall in case cache miss
    #                 response = self.memory_heirarchy[0].read((self.EX_MEM_ALUResult[1]))
    #                 if response == "wait":
    #                     self.MEM_WB_Stall[0] = 1
    #                 else:
    #                     self.MEM_WB_LWDataValue[0] = response[0]
    #                     self.MEM_WB_Stall[0] = 0
                    
    #         # If store (if you are writing to memory and you are not writing to register)
    #         elif(self.EX_MEM_MemWrite[1] == 1 and self.EX_MEM_RegWrite[1] == 0):
    #             # Stores are handled here
    #             self.MEM_WB_LWDataValue[0] = 0
                
    #             if (self.EX_MEM_Opcode[1] == 0x2B):
    #                 logging.info("[4] \tMEM: SW")
    #                 # stall in case cache miss
    #                 response = self.memory_heirarchy[0].write(self.EX_MEM_ALUResult[1], self.EX_MEM_SWValue[1])
    #                 if response == "wait":
    #                     self.MEM_WB_Stall[0] = 1
    #                 else:
    #                     self.MEM_WB_Stall[0] = 0

    #     # If instruction doesn't read or write from memory
    #     else:
    #         logging.info("[4] \tMEM: no memory access")
    #         pass
        
        
    # def WB(self):
    #     # During the Write Back stage, values are written back into registers 
    #     # if there are values to be written. For instructions such as stores  
    #     # and jumps, nothing is processed
        
    #     # If writing back to registers from ALU calculation
    #     if(self.MEM_WB_RegWrite[1] == 1 and self.MEM_WB_MemToReg[1] == 0):
    #         logging.info("[5] \t WB: write back from ALU")
    #         self.R[self.MEM_WB_WriteRegNum[1]] = self.MEM_WB_ALUResult[1]

    #     # If writing back to registers from memory
    #     elif(self.MEM_WB_RegWrite[1] == 1 and self.MEM_WB_MemToReg[1] == 1):
    #         logging.info("[5] \t WB: write back from memory")
    #         self.R[self.MEM_WB_WriteRegNum[1]] = self.MEM_WB_LWDataValue[1]

    #     else:
    #         logging.info("[5] \t WB: no write back")
    #         # no registers are written to in case of a noop or a stores
    #         pass
            
    # def copy_write_to_read(self):
    #     # During every step of the pipeline move values from write to read 
    #     # given that stall has not occured (managed in the IF stage)
        
    #     self.IF_ID_PC[1] = self.IF_ID_PC[0]
    #     self.IF_ID_Inst[1] = self.IF_ID_Inst[0]

    #     self.ID_EX_PC[1] = self.ID_EX_PC[0]
    #     self.ID_EX_ReadReg1Value[1] = self.ID_EX_ReadReg1Value[0]
    #     self.ID_EX_ReadReg2Value[1] = self.ID_EX_ReadReg2Value[0]
    #     self.ID_EX_SEOffset[1] = self.ID_EX_SEOffset[0]
    #     self.ID_EX_WriteReg_20_16[1] = self.ID_EX_WriteReg_20_16[0]
    #     self.ID_EX_WriteReg_15_11[1] = self.ID_EX_WriteReg_15_11[0]
    #     self.ID_EX_Opcode[1] = self.ID_EX_Opcode[0]
    #     self.ID_EX_Function[1] = self.ID_EX_Function[0]
    #     self.ID_EX_RegDst[1] = self.ID_EX_RegDst[0]
    #     self.ID_EX_ALUSrc[1] = self.ID_EX_ALUSrc[0]
    #     self.ID_EX_ALUOp1[1] = self.ID_EX_ALUOp1[0]
    #     self.ID_EX_ALUOp2[1] = self.ID_EX_ALUOp2[0]
    #     self.ID_EX_MemRead[1] = self.ID_EX_MemRead[0]
    #     self.ID_EX_MemWrite[1] = self.ID_EX_MemWrite[0]
    #     self.ID_EX_MemToReg[1] = self.ID_EX_MemToReg[0]
    #     self.ID_EX_RegWrite[1] = self.ID_EX_RegWrite[0]
    #     self.ID_EX_Target[1] = self.ID_EX_Target[0]
        
    #     self.EX_MEM_Zero[1] = self.EX_MEM_Zero[0]
    #     self.EX_MEM_ALUResult[1] = self.EX_MEM_ALUResult[0]
    #     self.EX_MEM_SWValue[1] = self.EX_MEM_SWValue[0]
    #     self.EX_MEM_WriteRegNum[1] = self.EX_MEM_WriteRegNum[0]
    #     self.EX_MEM_MemRead[1] = self.EX_MEM_MemRead[0]
    #     self.EX_MEM_MemWrite[1] = self.EX_MEM_MemWrite[0]
    #     self.EX_MEM_MemToReg[1] = self.EX_MEM_MemToReg[0]
    #     self.EX_MEM_RegWrite[1] = self.EX_MEM_RegWrite[0]
    #     self.EX_MEM_Opcode[1] = self.EX_MEM_Opcode[0]
        
    #     self.MEM_WB_LWDataValue[1] = self.MEM_WB_LWDataValue[0]
    #     self.MEM_WB_ALUResult[1] = self.MEM_WB_ALUResult[0]
    #     self.MEM_WB_WriteRegNum[1] = self.MEM_WB_WriteRegNum[0]
    #     self.MEM_WB_MemToReg[1] = self.MEM_WB_MemToReg[0]
    #     self.MEM_WB_RegWrite[1] = self.MEM_WB_RegWrite[0]
    #     self.MEM_WB_Stall[1] = self.MEM_WB_Stall[0]
        
        
    # def step(self):
    #     # step through the 5 stages of the pipeline
    #     # TODO: Should step just call WB, and WB call MEM, MEM call EX, etc?
    #     # Otherwise, if MEM is stalled, EX will still occur.
    #     self.WB()
    #     self.cycle += 1

    # def load_instructions(self, instructions):
    #     # TODO: Load and cache instructions rather than setting them as an attribute.
    #     self.instructions = instructions
    #     self.memory_heirarchy[-1].data[:len(instructions)] = instructions


    