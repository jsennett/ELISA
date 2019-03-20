# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:06:58 2019

@author: ayash
"""
from memory import Memory, Cache
from pprint import pprint
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
        # self.R = [0] * 32
        self.R = list(range(100, 132))
        self.F = [0] * 32
        self.PC = 0

        # Pipeline Buffers ([write, read] pairs)
        self.IF_ID_PC = [0] * 2
        self.IF_ID_Inst = [0] * 2
        self.ID_EX_PC = [0] * 2
        self.ID_EX_ReadReg1Value = [0] * 2
        self.ID_EX_ReadReg2Value = [0] * 2
        self.ID_EX_SEOffset = [0] * 2
        self.ID_EX_WriteReg_20_16 = [0] * 2
        self.ID_EX_WriteReg_15_11 = [0] * 2
        self.ID_EX_Opcode = [0] * 2
        self.ID_EX_Function = [0] * 2
        self.ID_EX_RegDst = [0] * 2
        self.ID_EX_ALUSrc = [0] * 2
        self.ID_EX_ALUOp1 = [0] * 2
        self.ID_EX_ALUOp2 = [0] * 2
        self.ID_EX_MemRead = [0] * 2
        self.ID_EX_MemWrite = [0] * 2
        self.ID_EX_MemToReg = [0] * 2
        self.ID_EX_RegWrite = [0] * 2
        self.ID_EX_Target = [0] * 2
        self.EX_MEM_Zero = [0] * 2
        self.EX_MEM_ALUResult = [0] * 2
        self.EX_MEM_SWValue = [0] * 2
        self.EX_MEM_WriteRegNum = [0] * 2
        self.EX_MEM_MemRead = [0] * 2
        self.EX_MEM_MemWrite = [0] * 2
        self.EX_MEM_MemToReg = [0] * 2
        self.EX_MEM_RegWrite = [0] * 2
        self.EX_MEM_Opcode = [0] * 2
        self.MEM_WB_LWDataValue = [0] * 2
        self.MEM_WB_ALUResult = [0] * 2
        self.MEM_WB_WriteRegNum = [0] * 2
        self.MEM_WB_MemToReg = [0] * 2
        self.MEM_WB_RegWrite = [0] * 2
        self.MEM_WB_Stall = [0] * 2

    def reset_memory(self):
        for level in self.memory_heirarchy:
            level.reset_data()

        
    def IF(self):
        # Get the instruction to be processed and pass it along to ID stage

        # If we finish the program:
        # TODO: Correctly implement when we finish a program.
        instruction_idx = self.IF_ID_PC[0]//4
        if instruction_idx >= len(self.instructions):
            logging.info("Program finished.")
            return

        # Display instruction meaning
        print("Loading instruction:", self.instruction_meanings[instruction_idx], bin(self.instructions[instruction_idx]))
        
        # If not a stall
        if(self.MEM_WB_Stall[0] == 0):
            logging.info("[1] \t IF: Fetch")

            # Move buffer register values to the right
            self.copy_write_to_read()
            
            self.IF_ID_Inst[0] = self.instructions[instruction_idx]
    
            # update PC
            # TODO: Don't replicate the PC in two variables.
            self.IF_ID_PC[0] += 4
            self.PC = self.IF_ID_PC[0]
        else:
            logging.info("[1] \t IF: Stall")

        
    def ID(self):
        # Parse out instruction and pass along values to EX stage
        # ID stage reads values from the register
        
        opcode = (self.IF_ID_Inst[1] & 0xFC000000) >> 26
        srcRegister = (self.IF_ID_Inst[1] & 0x03E00000) >> 21
        srcOrDestRegister = (self.IF_ID_Inst[1] & 0x001F0000) >> 16
        destRegister = (self.IF_ID_Inst[1] & 0x0000F800) >> 11
        
        self.ID_EX_PC[0] = self.IF_ID_PC[1]
        self.ID_EX_ReadReg1Value[0] = self.R[srcRegister]
        self.ID_EX_ReadReg2Value[0] = self.R[srcOrDestRegister]
        self.ID_EX_WriteReg_20_16[0] = srcOrDestRegister
        self.ID_EX_WriteReg_15_11[0] = destRegister
        self.ID_EX_Opcode[0] = opcode
        
        # If opcode 0, R format.
        if (opcode == 0):

            # Parse function code
            function = (self.IF_ID_Inst[1] & 0x0000003F)
            self.ID_EX_Function[0] = function

            # If ADD
            if (function == 0x20):
                logging.info("[2] \t ID: ADD")
                self.ID_EX_SEOffset[0] = 0
                self.ID_EX_RegDst[0] = 1
                self.ID_EX_ALUSrc[0] = 0
                self.ID_EX_ALUOp1[0] = 1
                self.ID_EX_ALUOp2[0] = 0
                self.ID_EX_MemRead[0] = 0
                self.ID_EX_MemWrite[0] = 0
                self.ID_EX_MemToReg[0] = 0
                self.ID_EX_RegWrite[0] = 1

            # If SUB
            elif (function == 0x22):
                logging.info("[2] \t ID: SUB")
                self.ID_EX_SEOffset[0] = 0
                self.ID_EX_RegDst[0] = 1
                self.ID_EX_ALUSrc[0] = 0
                self.ID_EX_ALUOp1[0] = 1
                self.ID_EX_ALUOp2[0] = 0
                self.ID_EX_MemRead[0] = 0
                self.ID_EX_MemWrite[0] = 0
                self.ID_EX_MemToReg[0] = 0
                self.ID_EX_RegWrite[0] = 1

            # If NOP
            elif(function == 0x0):
                logging.info("[2] \t ID: NOP")
                self.ID_EX_ReadReg1Value[0] = 0
                self.ID_EX_ReadReg2Value[0] = 0
                self.ID_EX_SEOffset[0] = 0
                self.ID_EX_WriteReg_20_16[0] = 0
                self.ID_EX_WriteReg_15_11[0] = 0
                self.ID_EX_RegDst[0] = 0
                self.ID_EX_ALUSrc[0] = 0
                self.ID_EX_ALUOp1[0] = 0
                self.ID_EX_ALUOp2[0] = 0
                self.ID_EX_MemRead[0] = 0
                self.ID_EX_MemWrite[0] = 0
                self.ID_EX_MemToReg[0] = 0
                self.ID_EX_RegWrite[0] = 0

            else:
                logging.info("[2] \t ID: other / uncoded")

                # TODO: Support additional R type instructions
                # TODO: Support JR (jump to register)
                pass
            
        # If I-Format or J-Format
        else:

            # parse and sign extend the immediate value
            immediate = (self.IF_ID_Inst[1] & 0x0000FFFF)
            if (immediate >> 15 == 1):
                immediate = -1*(immediate ^ 0xFFFF)-1
            
            # If LW
            if(opcode == 0x23):
                logging.info("[2] \t ID: LW")
                self.ID_EX_SEOffset[0] = immediate
                self.ID_EX_Function[0] = 0
                self.ID_EX_RegDst[0] = 0
                self.ID_EX_ALUSrc[0] = 1
                self.ID_EX_ALUOp1[0] = 0
                self.ID_EX_ALUOp2[0] = 0
                self.ID_EX_MemRead[0] = 1
                self.ID_EX_MemWrite[0] = 0
                self.ID_EX_MemToReg[0] = 1
                self.ID_EX_RegWrite[0] = 1

            # If SW
            elif(opcode == 0x2B):
                logging.info("[2] \t ID: SW")
                self.ID_EX_SEOffset[0] = immediate
                self.ID_EX_Function[0] = 0
                self.ID_EX_RegDst[0] = 0
                self.ID_EX_ALUSrc[0] = 1
                self.ID_EX_ALUOp1[0] = 0
                self.ID_EX_ALUOp2[0] = 0
                self.ID_EX_MemRead[0] = 0
                self.ID_EX_MemWrite[0] = 1
                self.ID_EX_MemToReg[0] = 0
                self.ID_EX_RegWrite[0] = 0

            # If neither LW or SW, it is a J-Type
            else:
            
                # Parse target (last 26 bits of J-Type instruction)
                self.ID_EX_Target[0] = (self.IF_ID_Inst[1] & 0x03FFFFFF)

                # If J (jump) or JAL (jump and link)
                if opcode == 0x02:
                    logging.info("[2] \t ID: J")
                    self.IF_ID_Inst[0] = 0x00000000
                elif opcode == 0x03:
                    logging.info("[2] \t ID: JAL")
                    self.IF_ID_Inst[0] = 0x00000000
                else:
                    # Noop
                    logging.info("[2] \t ID: Opcode not found")
                    pass
        
        
    def EX(self):
        # The execute stage calculates relevant values using the ALU. It either
        # calculates the operation or an address for loading, storing, or 
        # jumping
        
        # Pass along values
        self.EX_MEM_Opcode[0] = self.ID_EX_Opcode[1]
        
        # R-format
        # If ADD
        if (self.ID_EX_Function[1] == 0x20):
            logging.info("[3] \t EX: ADD")
            self.EX_MEM_Zero[0] = 0xf
            self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + self.ID_EX_ReadReg2Value[1]
            self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
            self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_15_11[1]

            self.EX_MEM_MemRead[0] = 0
            self.EX_MEM_MemWrite[0] = 0
            self.EX_MEM_MemToReg[0] = 0
            self.EX_MEM_RegWrite[0] = 1
            
        # If SUB
        elif (self.ID_EX_Function[1] == 0x22):
            logging.info("[3] \t EX: SUB")
            self.EX_MEM_Zero[0] = 0xf
            self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] - (self.ID_EX_ReadReg2Value[1])
            self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
            self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_15_11[1]

            self.EX_MEM_MemRead[0] = 0
            self.EX_MEM_MemWrite[0] = 0
            self.EX_MEM_MemToReg[0] = 0
            self.EX_MEM_RegWrite[0] = 1
            
        # I format
        else:
            # If LB
            if(self.ID_EX_Opcode[1] == 0x20 and self.ID_EX_MemWrite[1] == 0 and self.ID_EX_MemToReg[1] == 1):
                logging.info("[3] \t EX: LB")
                self.EX_MEM_Zero[0] = 0xf
                self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
                self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
                self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_20_16[1]
    
                self.EX_MEM_MemRead[0] = 1
                self.EX_MEM_MemWrite[0] = 0
                self.EX_MEM_MemToReg[0] = 1
                self.EX_MEM_RegWrite[0] = 1
            
            # If SB
            elif (self.ID_EX_Opcode[1] == 0x28 and self.ID_EX_MemWrite[1] == 1):
                logging.info("[3] \t EX: SB")
                self.EX_MEM_Zero[0] = 0xf;
                self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
                self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
                self.EX_MEM_WriteRegNum[0] = 0
    
                self.EX_MEM_MemRead[0] = 0
                self.EX_MEM_MemWrite[0] = 1
                self.EX_MEM_MemToReg[0] = 0
                self.EX_MEM_RegWrite[0] = 0
            
            # If LW
            elif(self.ID_EX_Opcode[1] == 0x23 and self.ID_EX_MemWrite[1] == 0 and self.ID_EX_MemToReg[1] == 1):
                logging.info("[3] \t EX: LW")
                self.EX_MEM_Zero[0] = 0xf
                self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
                self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
                self.EX_MEM_WriteRegNum[0] = self.ID_EX_WriteReg_20_16[1]
    
                self.EX_MEM_MemRead[0] = 1
                self.EX_MEM_MemWrite[0] = 0
                self.EX_MEM_MemToReg[0] = 1
                self.EX_MEM_RegWrite[0] = 1
            
            # If SW
            elif (self.ID_EX_Opcode[1] == 0x2B and self.ID_EX_MemWrite[1] == 1):
                logging.info("[3] \t EX: SW")
                self.EX_MEM_Zero[0] = 0xf;
                self.EX_MEM_ALUResult[0] = self.ID_EX_ReadReg1Value[1] + (self.ID_EX_SEOffset[1]<<2)
                self.EX_MEM_SWValue[0] = self.ID_EX_ReadReg2Value[1]
                self.EX_MEM_WriteRegNum[0] = 0
    
                self.EX_MEM_MemRead[0] = 0
                self.EX_MEM_MemWrite[0] = 1
                self.EX_MEM_MemToReg[0] = 0
                self.EX_MEM_RegWrite[0] = 0
                
            else:
                # If J or JAL
                if (self.ID_EX_Opcode[1] == 0x02 or self.ID_EX_Opcode[1] == 0x03):
                    logging.info("[3] \t EX: J or JAL")

                    # Calculate the address and change PC and instruction
                    self.IF_ID_PC[0] = (self.IF_ID_PC[0] & 0xF0000000) ^ (self.ID_EX_Target[1]<<2)

                    # If we finish the program:
                    # TODO: Correctly implement when we finish a program.
                    instruction_idx = self.IF_ID_PC[0]//4
                    if instruction_idx >= len(self.instructions):
                        logging.info("Program finished.")
                        return

                    self.IF_ID_Inst[0] = self.instructions[self.IF_ID_PC[0]//4]
                    self.IF_ID_PC[0] += 4
                    self.PC = self.IF_ID_PC[0]
                    
                    # Todo: More work needed for Jump and link (JAL): set return register to the link address
                    
                # If NOP
                else:
                    logging.info("[3] \t EX: NOP")
                    self.EX_MEM_MemRead[0] = 0
                    self.EX_MEM_MemWrite[0] = 0
                    self.EX_MEM_MemToReg[0] = 0
                    self.EX_MEM_RegWrite[0] = 0
                    
                    self.EX_MEM_Zero[0] = 0
                    self.EX_MEM_ALUResult[0] = 0
                    self.EX_MEM_SWValue[0] = 0
                    self.EX_MEM_WriteRegNum[0] = 0
            
            
    def MEM(self):
        # The Ememory stage accesses the main memory. It first attempts to get
        # the write or read from cache within 1 clock cycle (changable), 
        # and if it cannot, a stall is incurred
        
        # Transfer control bits from the execute stage into the memory stage.
        self.MEM_WB_ALUResult[0] = self.EX_MEM_ALUResult[1]
        self.MEM_WB_WriteRegNum[0] = self.EX_MEM_WriteRegNum[1]
        self.MEM_WB_MemToReg[0] = self.EX_MEM_MemToReg[1]
        self.MEM_WB_RegWrite[0] = self.EX_MEM_RegWrite[1]
        
        # If the instruction is a read or write from memory
        if(self.EX_MEM_MemRead[1] == 1 or self.EX_MEM_MemWrite[1] == 1):
            
            # If load (if you are reading from memory and if you are writing to register)
            if (self.EX_MEM_MemRead[1] == 1 and self.EX_MEM_RegWrite[1] == 1):
                
                # If LW
                if(self.EX_MEM_Opcode[1] == 0x23):
                    logging.info("[4] \tMEM: LW")

                    # stall in case cache miss
                    response = self.memory_heirarchy[0].read((self.EX_MEM_ALUResult[1]))
                    if response == "wait":
                        self.MEM_WB_Stall[0] = 1
                    else:
                        self.MEM_WB_LWDataValue[0] = response[0]
                        self.MEM_WB_Stall[0] = 0
                    
            # If store (if you are writing to memory and you are not writing to register)
            elif(self.EX_MEM_MemWrite[1] == 1 and self.EX_MEM_RegWrite[1] == 0):
                # Stores are handled here
                self.MEM_WB_LWDataValue[0] = 0
                
                if (self.EX_MEM_Opcode[1] == 0x2B):
                    logging.info("[4] \tMEM: SW")
                    # stall in case cache miss
                    response = self.memory_heirarchy[0].write(self.EX_MEM_ALUResult[1], self.EX_MEM_SWValue[1])
                    if response == "wait":
                        self.MEM_WB_Stall[0] = 1
                    else:
                        self.MEM_WB_Stall[0] = 0

        # If instruction doesn't read or write from memory
        else:
            logging.info("[4] \tMEM: no memory access")
            pass
        
        
    def WB(self):
        # During the Write Back stage, values are written back into registers 
        # if there are values to be written. For instructions such as stores  
        # and jumps, nothing is processed
        
        # If writing back to registers from ALU calculation
        if(self.MEM_WB_RegWrite[1] == 1 and self.MEM_WB_MemToReg[1] == 0):
            logging.info("[5] \t WB: write back from ALU")
            self.R[self.MEM_WB_WriteRegNum[1]] = self.MEM_WB_ALUResult[1]

        # If writing back to registers from memory
        elif(self.MEM_WB_RegWrite[1] == 1 and self.MEM_WB_MemToReg[1] == 1):
            logging.info("[5] \t WB: write back from memory")
            self.R[self.MEM_WB_WriteRegNum[1]] = self.MEM_WB_LWDataValue[1]

        else:
            logging.info("[5] \t WB: no write back")
            # no registers are written to in case of a noop or a stores
            pass
            
    def copy_write_to_read(self):
        # During every step of the pipeline move values from write to read 
        # given that stall has not occured (managed in the IF stage)
        
        self.IF_ID_PC[1] = self.IF_ID_PC[0]
        self.IF_ID_Inst[1] = self.IF_ID_Inst[0]

        self.ID_EX_PC[1] = self.ID_EX_PC[0]
        self.ID_EX_ReadReg1Value[1] = self.ID_EX_ReadReg1Value[0]
        self.ID_EX_ReadReg2Value[1] = self.ID_EX_ReadReg2Value[0]
        self.ID_EX_SEOffset[1] = self.ID_EX_SEOffset[0]
        self.ID_EX_WriteReg_20_16[1] = self.ID_EX_WriteReg_20_16[0]
        self.ID_EX_WriteReg_15_11[1] = self.ID_EX_WriteReg_15_11[0]
        self.ID_EX_Opcode[1] = self.ID_EX_Opcode[0]
        self.ID_EX_Function[1] = self.ID_EX_Function[0]
        self.ID_EX_RegDst[1] = self.ID_EX_RegDst[0]
        self.ID_EX_ALUSrc[1] = self.ID_EX_ALUSrc[0]
        self.ID_EX_ALUOp1[1] = self.ID_EX_ALUOp1[0]
        self.ID_EX_ALUOp2[1] = self.ID_EX_ALUOp2[0]
        self.ID_EX_MemRead[1] = self.ID_EX_MemRead[0]
        self.ID_EX_MemWrite[1] = self.ID_EX_MemWrite[0]
        self.ID_EX_MemToReg[1] = self.ID_EX_MemToReg[0]
        self.ID_EX_RegWrite[1] = self.ID_EX_RegWrite[0]
        self.ID_EX_Target[1] = self.ID_EX_Target[0]
        
        self.EX_MEM_Zero[1] = self.EX_MEM_Zero[0]
        self.EX_MEM_ALUResult[1] = self.EX_MEM_ALUResult[0]
        self.EX_MEM_SWValue[1] = self.EX_MEM_SWValue[0]
        self.EX_MEM_WriteRegNum[1] = self.EX_MEM_WriteRegNum[0]
        self.EX_MEM_MemRead[1] = self.EX_MEM_MemRead[0]
        self.EX_MEM_MemWrite[1] = self.EX_MEM_MemWrite[0]
        self.EX_MEM_MemToReg[1] = self.EX_MEM_MemToReg[0]
        self.EX_MEM_RegWrite[1] = self.EX_MEM_RegWrite[0]
        self.EX_MEM_Opcode[1] = self.EX_MEM_Opcode[0]
        
        self.MEM_WB_LWDataValue[1] = self.MEM_WB_LWDataValue[0]
        self.MEM_WB_ALUResult[1] = self.MEM_WB_ALUResult[0]
        self.MEM_WB_WriteRegNum[1] = self.MEM_WB_WriteRegNum[0]
        self.MEM_WB_MemToReg[1] = self.MEM_WB_MemToReg[0]
        self.MEM_WB_RegWrite[1] = self.MEM_WB_RegWrite[0]
        self.MEM_WB_Stall[1] = self.MEM_WB_Stall[0]
        
        
    def step(self):
        # step through the 5 stages of the pipeline
        # TODO: Should step just call WB, and WB call MEM, MEM call EX, etc?
        # Otherwise, if MEM is stalled, EX will still occur.
        self.IF()
        self.ID()
        self.EX()
        self.MEM()
        self.WB()
        self.cycle += 1

    def load_instructions(self, instructions, instruction_meanings):
        # TODO: Remove redundancy, maybe fetch each instruction from memory
        # so that it gets cached.
        # TODO: remove instruction_meanings argument once we have an assembler
        self.memory_heirarchy[-1].data[:len(instructions)] = instructions
        self.instructions = instructions
        self.instruction_meanings = instruction_meanings


def main():
    
    # Get instructions (Not part of memory)
    instructions_to_meanings = [
        (0x00831820, "ADD $R3, $R4, $R3"),
        (0x01263820, "ADD $R7, $R9, $R6"),
        (0x00000000, "NOP"),
        (0x01224820, "ADD $R9, $R9, $R2"),
        (0x00624022, "SUB $R8, $R3, $R2"),
        (0x00000000, "NOP"),
        (0x8D48FFFC, "LW $R8, -4($R10)"),
    ]
    instructions = [pair[0] for pair in instructions_to_meanings]
    instruction_meanings = [pair[1] for pair in instructions_to_meanings]
    
    # Run instructions
    simulator = Simulator()
    simulator.load_instructions(instructions, instruction_meanings)

    # Step until instructions complete
    for _ in range(20):
        simulator.step()
        input()
    
if __name__ == '__main__':
    main()
    
    