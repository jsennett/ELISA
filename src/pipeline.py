# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:06:58 2019

@author: ayash
"""
from memory import Memory, Cache
import os


class Pipeline_Simulator:
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
        
         # Set memory and registers
        self.DRAM = Memory(lines=2**8, delay=3, noisy=False, name="DRAM")
        self.L3 = Cache(lines=2**5, words_per_line=4, delay=1, next_level=self.DRAM, noisy=False, name="L3")
        self.L2 = Cache(lines=2**5, words_per_line=4, delay=1, next_level=self.L3, noisy=False, name="L2")
        self.L1 = Cache(lines=8, words_per_line=4, delay=1, next_level=self.L2, noisy=False, name="L1")
        self.memory_heirarchy = [self.L1, self.L2, self.L3, self.DRAM]
        
        self.register = [0x0] * 32
        
        # Initialize the pipeline registers to 0. 
        # The pipeline registers exist as buffers between any two stages of the
        # pipline. At index 0 (left), values are written from the first stage
        # and at index 1 (right) values are read from the next stage.
        # Example: IF_IDReg_PC[0] is written to by the Instruction Fetch (IF) 
        # stage and IF_IDReg_PC[1] is read by the Instruction Decode (ID) stage
        self.IF_IDReg_PC = [0] * 2
        self.IF_IDReg_Inst = [0] * 2

        self.ID_EXReg_PC = [0] * 2
        self.ID_EXReg_ReadReg1Value = [0] * 2
        self.ID_EXReg_ReadReg2Value = [0] * 2
        self.ID_EXReg_SEOffset = [0] * 2
        self.ID_EXReg_WriteReg_20_16 = [0] * 2
        self.ID_EXReg_WriteReg_15_11 = [0] * 2
        self.ID_EXReg_Opcode = [0] * 2
        self.ID_EXReg_Function = [0] * 2
        self.ID_EXReg_RegDst = [0] * 2
        self.ID_EXReg_ALUSrc = [0] * 2
        self.ID_EXReg_ALUOp1 = [0] * 2
        self.ID_EXReg_ALUOp2 = [0] * 2
        self.ID_EXReg_MemRead = [0] * 2
        self.ID_EXReg_MemWrite = [0] * 2
        self.ID_EXReg_MemToReg = [0] * 2
        self.ID_EXReg_RegWrite = [0] * 2
        self.ID_EXReg_Target = [0] * 2
        
        self.EX_MEMReg_Zero = [0] * 2
        self.EX_MEMReg_ALUResult = [0] * 2
        self.EX_MEMReg_SWValue = [0] * 2
        self.EX_MEMReg_WriteRegNum = [0] * 2
        self.EX_MEMReg_MemRead = [0] * 2
        self.EX_MEMReg_MemWrite = [0] * 2
        self.EX_MEMReg_MemToReg = [0] * 2
        self.EX_MEMReg_RegWrite = [0] * 2
        self.EX_MEMReg_Opcode = [0] * 2

        self.MEM_WBReg_LWDataValue = [0] * 2
        self.MEM_WBReg_ALUResult = [0] * 2
        self.MEM_WBReg_WriteRegNum = [0] * 2
        self.MEM_WBReg_MemToReg = [0] * 2
        self.MEM_WBReg_RegWrite = [0] * 2
        self.MEM_WBReg_Stall = [0] * 2
        
    
    def IF_stage(self, instruction_set):
        # Get the instruction to be processed and pass it along to ID stage
        # update PC
        
        # Handle stalls here - do not proceed if we are stalling
        if(self.MEM_WBReg_Stall[0] == 0):
            self.Copy_write_to_read()
            
            self.IF_IDReg_Inst[0] = instruction_set[self.IF_IDReg_PC[0]//4]
            self.IF_IDReg_PC[0] += 4
        
    def ID_stage(self):
        # Parse out instruction and pass along values to EX stage
        # ID stage reads values from the register
        
        opcode = (self.IF_IDReg_Inst[1] & 0xFC000000) >> 26
        srcRegister = (self.IF_IDReg_Inst[1] & 0x03E00000) >> 21
        srcOrDestRegister = (self.IF_IDReg_Inst[1] & 0x001F0000) >> 16
        destRegister = (self.IF_IDReg_Inst[1] & 0x0000F800) >> 11
        
        self.ID_EXReg_PC[0] = self.IF_IDReg_PC[1]
        self.ID_EXReg_ReadReg1Value[0] = self.register[srcRegister]
        self.ID_EXReg_ReadReg2Value[0] = self.register[srcOrDestRegister]
        self.ID_EXReg_WriteReg_20_16[0] = srcOrDestRegister
        self.ID_EXReg_WriteReg_15_11[0] = destRegister
        self.ID_EXReg_Opcode[0] = opcode
        
        if (opcode == 0):
            # This is the R-Format
            function = (self.IF_IDReg_Inst[1] & 0x0000003F)
            self.ID_EXReg_Function[0] = function
            # Use given format
            if (function == 0x20):
                # addition
                self.ID_EXReg_SEOffset[0] = 0
                self.ID_EXReg_RegDst[0] = 1
                self.ID_EXReg_ALUSrc[0] = 0
                self.ID_EXReg_ALUOp1[0] = 1
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 0
                self.ID_EXReg_MemWrite[0] = 0
                self.ID_EXReg_MemToReg[0] = 0
                self.ID_EXReg_RegWrite[0] = 1
            elif (function == 0x22):
                # subtraction
                self.ID_EXReg_SEOffset[0] = 0
                self.ID_EXReg_RegDst[0] = 1
                self.ID_EXReg_ALUSrc[0] = 0
                self.ID_EXReg_ALUOp1[0] = 1
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 0
                self.ID_EXReg_MemWrite[0] = 0
                self.ID_EXReg_MemToReg[0] = 0
                self.ID_EXReg_RegWrite[0] = 1
            elif(function == 0x0):
                # noop
                self.ID_EXReg_ReadReg1Value[0] = 0
                self.ID_EXReg_ReadReg2Value[0] = 0
                self.ID_EXReg_SEOffset[0] = 0
                self.ID_EXReg_WriteReg_20_16[0] = 0
                self.ID_EXReg_WriteReg_15_11[0] = 0
                self.ID_EXReg_RegDst[0] = 0
                self.ID_EXReg_ALUSrc[0] = 0
                self.ID_EXReg_ALUOp1[0] = 0
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 0
                self.ID_EXReg_MemWrite[0] = 0
                self.ID_EXReg_MemToReg[0] = 0
                self.ID_EXReg_RegWrite[0] = 0
            else:
                # do nothing
                pass
            
        else:
            # This is the I-Format or J-format decided by the OPCODE
            
            # parse and sign extend the immediate value
            immediate = (self.IF_IDReg_Inst[1] & 0x0000FFFF)
            if (immediate >> 15 == 1):
                immediate = -1*(immediate ^ 0xFFFF)-1
            
            # MIPS driven Opcodes
            if (opcode == 0x20):
                # lb
                self.ID_EXReg_SEOffset[0] = immediate
                self.ID_EXReg_Function[0] = 0
                self.ID_EXReg_RegDst[0] = 0
                self.ID_EXReg_ALUSrc[0] = 1
                self.ID_EXReg_ALUOp1[0] = 0
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 1
                self.ID_EXReg_MemWrite[0] = 0
                self.ID_EXReg_MemToReg[0] = 1
                self.ID_EXReg_RegWrite[0] = 1
            elif(opcode == 0x28):
                # sb
                self.ID_EXReg_SEOffset[0] = immediate
                self.ID_EXReg_Function[0] = 0
                self.ID_EXReg_RegDst[0] = 0
                self.ID_EXReg_ALUSrc[0] = 1
                self.ID_EXReg_ALUOp1[0] = 0
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 0
                self.ID_EXReg_MemWrite[0] = 1
                self.ID_EXReg_MemToReg[0] = 0
                self.ID_EXReg_RegWrite[0] = 0
            elif(opcode == 0x23):
                # lw
                self.ID_EXReg_SEOffset[0] = immediate
                self.ID_EXReg_Function[0] = 0
                self.ID_EXReg_RegDst[0] = 0
                self.ID_EXReg_ALUSrc[0] = 1
                self.ID_EXReg_ALUOp1[0] = 0
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 1
                self.ID_EXReg_MemWrite[0] = 0
                self.ID_EXReg_MemToReg[0] = 1
                self.ID_EXReg_RegWrite[0] = 1
            elif(opcode == 0x2B):
                # sw
                self.ID_EXReg_SEOffset[0] = immediate
                self.ID_EXReg_Function[0] = 0
                self.ID_EXReg_RegDst[0] = 0
                self.ID_EXReg_ALUSrc[0] = 1
                self.ID_EXReg_ALUOp1[0] = 0
                self.ID_EXReg_ALUOp2[0] = 0
                self.ID_EXReg_MemRead[0] = 0
                self.ID_EXReg_MemWrite[0] = 1
                self.ID_EXReg_MemToReg[0] = 0
                self.ID_EXReg_RegWrite[0] = 0
            else:
                # The rest of Opcodes are J-type formats
                self.ID_EXReg_Target[0] = (self.IF_IDReg_Inst[1] & 0x03FFFFFF)
                if (opcode == 0x02 or opcode == 0x03):
                    # Jump instruction: flush instruction loaded in the IF 
                    # stage (both Jump to link and address)
                    self.IF_IDReg_Inst[0] = 0x00000000
                else:
                    # Noop
                    pass
        
        
    def EX_stage(self):
        # The execute stage calculates relevant values using the ALU. It either
        # calculates the operation or an address for loading, storing, or 
        # jumping
        
        # Pass along values
        self.EX_MEMReg_Opcode[0] = self.ID_EXReg_Opcode[1]
        
        # R-format
        if (self.ID_EXReg_Function[1] == 0x20):
            # Addition
            self.EX_MEMReg_Zero[0] = 0xf
            self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_ReadReg2Value[1]
            self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
            self.EX_MEMReg_WriteRegNum[0] = self.ID_EXReg_WriteReg_15_11[1]

            self.EX_MEMReg_MemRead[0] = 0
            self.EX_MEMReg_MemWrite[0] = 0
            self.EX_MEMReg_MemToReg[0] = 0
            self.EX_MEMReg_RegWrite[0] = 1
            
        elif (self.ID_EXReg_Function[1] == 0x22):
            # TODO: Fix subtraction
            # Subtraction
            print('sub\n')
            self.EX_MEMReg_Zero[0] = 0xf
            self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + (self.ID_EXReg_ReadReg2Value[1] + 1)
            self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
            self.EX_MEMReg_WriteRegNum[0] = self.ID_EXReg_WriteReg_15_11[1]

            self.EX_MEMReg_MemRead[0] = 0
            self.EX_MEMReg_MemWrite[0] = 0
            self.EX_MEMReg_MemToReg[0] = 0
            self.EX_MEMReg_RegWrite[0] = 1
            
        else:
            # I format
            if(self.ID_EXReg_Opcode[1] == 0x20 and self.ID_EXReg_MemWrite[1] == 0 and self.ID_EXReg_MemToReg[1] == 1):
                # LB
                self.EX_MEMReg_Zero[0] = 0xf
                self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_SEOffset[1]>>2
                self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
                self.EX_MEMReg_WriteRegNum[0] = self.ID_EXReg_WriteReg_20_16[1]
    
                self.EX_MEMReg_MemRead[0] = 1
                self.EX_MEMReg_MemWrite[0] = 0
                self.EX_MEMReg_MemToReg[0] = 1
                self.EX_MEMReg_RegWrite[0] = 1
            
            elif (self.ID_EXReg_Opcode[1] == 0x28 and self.ID_EXReg_MemWrite[1] == 1):
                # SB
                self.EX_MEMReg_Zero[0] = 0xf;
                self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_SEOffset[1]>>2
                self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
                self.EX_MEMReg_WriteRegNum[0] = 0
    
                self.EX_MEMReg_MemRead[0] = 0
                self.EX_MEMReg_MemWrite[0] = 1
                self.EX_MEMReg_MemToReg[0] = 0
                self.EX_MEMReg_RegWrite[0] = 0
            
            elif(self.ID_EXReg_Opcode[1] == 0x23 and self.ID_EXReg_MemWrite[1] == 0 and self.ID_EXReg_MemToReg[1] == 1):
                # LW
                self.EX_MEMReg_Zero[0] = 0xf
                self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_SEOffset[1]>>2
                self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
                self.EX_MEMReg_WriteRegNum[0] = self.ID_EXReg_WriteReg_20_16[1]
    
                self.EX_MEMReg_MemRead[0] = 1
                self.EX_MEMReg_MemWrite[0] = 0
                self.EX_MEMReg_MemToReg[0] = 1
                self.EX_MEMReg_RegWrite[0] = 1
            
            elif (self.ID_EXReg_Opcode[1] == 0x2B and self.ID_EXReg_MemWrite[1] == 1):
                # SW
                self.EX_MEMReg_Zero[0] = 0xf;
                self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_SEOffset[1]>>2
                self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
                self.EX_MEMReg_WriteRegNum[0] = 0
    
                self.EX_MEMReg_MemRead[0] = 0
                self.EX_MEMReg_MemWrite[0] = 1
                self.EX_MEMReg_MemToReg[0] = 0
                self.EX_MEMReg_RegWrite[0] = 0
                
            else:
                if (self.ID_EXReg_Opcode[1] == 0x02 or self.ID_EXReg_Opcode[1] == 0x03):
                    # Calculate the address and change PC and instruction
                    self.IF_IDReg_PC[0] = (self.IF_IDReg_PC[0] & 0xF0000000) ^ (self.ID_EXReg_Target[1]<<2)
                    self.IF_IDReg_Inst[0] = instruction_set[self.IF_IDReg_PC[0]//4]
                    self.IF_IDReg_PC[0] += 4
                    
                    # Todo: More work needed for Jump and link (JAL)
                    
                else:
                    #NoOP
                    self.EX_MEMReg_MemRead[0] = 0
                    self.EX_MEMReg_MemWrite[0] = 0
                    self.EX_MEMReg_MemToReg[0] = 0
                    self.EX_MEMReg_RegWrite[0] = 0
                    
                    self.EX_MEMReg_Zero[0] = 0
                    self.EX_MEMReg_ALUResult[0] = 0
                    self.EX_MEMReg_SWValue[0] = 0
                    self.EX_MEMReg_WriteRegNum[0] = 0
            
            
    def Mem_stage(self, Main_Mem):
        # The Ememory stage accesses the main memory. It first attempts to get
        # the write or read from cache within 1 clock cycle (changable), 
        # and if it cannot, a stall is incurred
        
        # index into main memory if instruction is an lb. For everything else, pass the data along in the pipeline
        self.MEM_WBReg_ALUResult[0] = self.EX_MEMReg_ALUResult[1]
        self.MEM_WBReg_WriteRegNum[0] = self.EX_MEMReg_WriteRegNum[1]
        self.MEM_WBReg_MemToReg[0] = self.EX_MEMReg_MemToReg[1]
        self.MEM_WBReg_RegWrite[0] = self.EX_MEMReg_RegWrite[1]
        
        if(self.EX_MEMReg_MemRead[1] == 1 or self.EX_MEMReg_MemWrite[1] == 1):
            # Access memory for reading or writing
            
            if (self.EX_MEMReg_MemRead[1] == 1 and self.EX_MEMReg_RegWrite[1] == 1):
                # loads are handled here
                if(self.EX_MEMReg_Opcode[1] == 0x20):
                    # LB
                    self.MEM_WBReg_LWDataValue[0] = Main_Mem[(self.EX_MEMReg_ALUResult[1])]
                
                elif(self.EX_MEMReg_Opcode[1] == 0x23):
                    # LW
                    # stall in case cache miss
                    response = self.memory_heirarchy[0].read((self.EX_MEMReg_ALUResult[1]))
                    if response == "wait":
                        self.MEM_WBReg_Stall[0] = 1
                    else:
                        self.MEM_WBReg_LWDataValue[0] = response[0]
                        self.MEM_WBReg_Stall[0] = 0
                    
            elif(self.EX_MEMReg_MemWrite[1] == 1 and self.EX_MEMReg_RegWrite[1] == 0):
                # Stores are handled here
                self.MEM_WBReg_LWDataValue[0] = 0
                if (self.EX_MEMReg_Opcode[1] == 0x28):
                    # write back to main memory
                    Main_Mem[(self.EX_MEMReg_ALUResult[1])] = self.EX_MEMReg_SWValue[1]
                    
                elif (self.EX_MEMReg_Opcode[1] == 0x2B):
                    # SW
                    # stall in case cache miss
                    response = self.memory_heirarchy[0].write(self.EX_MEMReg_ALUResult[1], self.EX_MEMReg_SWValue[1])
                    if response == "wait":
                        self.MEM_WBReg_Stall[0] = 1
                    else:
                        self.MEM_WBReg_Stall[0] = 0
        else:
            # No access to memory needed
            pass
        
        
    def WriteBack_stage(self, Main_Mem):
        # During the Write Back stage, values are written back into registers 
        # if there are values to be written. For instructions such as stores  
        # and jumps, nothing is processed
        
        if(self.MEM_WBReg_RegWrite[1] == 1 and self.MEM_WBReg_MemToReg[1] == 0):
            # writing back to registers from ALU calculation
            self.register[self.MEM_WBReg_WriteRegNum[1]] = self.MEM_WBReg_ALUResult[1]
        elif(self.MEM_WBReg_RegWrite[1] == 1 and self.MEM_WBReg_MemToReg[1] == 1):
            # Writing back to registers from memory
            self.register[self.MEM_WBReg_WriteRegNum[1]] = self.MEM_WBReg_LWDataValue[1]
        else:
            # no registers are written to in case of a noop or a stores
            pass
            
    def Copy_write_to_read(self):
        # During every step of the pipeline move values from write to read 
        # given that stall has not occured (managed in the IF stage)
        
        self.IF_IDReg_PC[1] = self.IF_IDReg_PC[0]
        self.IF_IDReg_Inst[1] = self.IF_IDReg_Inst[0]

        self.ID_EXReg_PC[1] = self.ID_EXReg_PC[0]
        self.ID_EXReg_ReadReg1Value[1] = self.ID_EXReg_ReadReg1Value[0]
        self.ID_EXReg_ReadReg2Value[1] = self.ID_EXReg_ReadReg2Value[0]
        self.ID_EXReg_SEOffset[1] = self.ID_EXReg_SEOffset[0]
        self.ID_EXReg_WriteReg_20_16[1] = self.ID_EXReg_WriteReg_20_16[0]
        self.ID_EXReg_WriteReg_15_11[1] = self.ID_EXReg_WriteReg_15_11[0]
        self.ID_EXReg_Opcode[1] = self.ID_EXReg_Opcode[0]
        self.ID_EXReg_Function[1] = self.ID_EXReg_Function[0]
        self.ID_EXReg_RegDst[1] = self.ID_EXReg_RegDst[0]
        self.ID_EXReg_ALUSrc[1] = self.ID_EXReg_ALUSrc[0]
        self.ID_EXReg_ALUOp1[1] = self.ID_EXReg_ALUOp1[0]
        self.ID_EXReg_ALUOp2[1] = self.ID_EXReg_ALUOp2[0]
        self.ID_EXReg_MemRead[1] = self.ID_EXReg_MemRead[0]
        self.ID_EXReg_MemWrite[1] = self.ID_EXReg_MemWrite[0]
        self.ID_EXReg_MemToReg[1] = self.ID_EXReg_MemToReg[0]
        self.ID_EXReg_RegWrite[1] = self.ID_EXReg_RegWrite[0]
        self.ID_EXReg_Target[1] = self.ID_EXReg_Target[0]
        
        self.EX_MEMReg_Zero[1] = self.EX_MEMReg_Zero[0]
        self.EX_MEMReg_ALUResult[1] = self.EX_MEMReg_ALUResult[0]
        self.EX_MEMReg_SWValue[1] = self.EX_MEMReg_SWValue[0]
        self.EX_MEMReg_WriteRegNum[1] = self.EX_MEMReg_WriteRegNum[0]
        self.EX_MEMReg_MemRead[1] = self.EX_MEMReg_MemRead[0]
        self.EX_MEMReg_MemWrite[1] = self.EX_MEMReg_MemWrite[0]
        self.EX_MEMReg_MemToReg[1] = self.EX_MEMReg_MemToReg[0]
        self.EX_MEMReg_RegWrite[1] = self.EX_MEMReg_RegWrite[0]
        self.EX_MEMReg_Opcode[1] = self.EX_MEMReg_Opcode[0]
        
        self.MEM_WBReg_LWDataValue[1] = self.MEM_WBReg_LWDataValue[0]
        self.MEM_WBReg_ALUResult[1] = self.MEM_WBReg_ALUResult[0]
        self.MEM_WBReg_WriteRegNum[1] = self.MEM_WBReg_WriteRegNum[0]
        self.MEM_WBReg_MemToReg[1] = self.MEM_WBReg_MemToReg[0]
        self.MEM_WBReg_RegWrite[1] = self.MEM_WBReg_RegWrite[0]
        self.MEM_WBReg_Stall[1] = self.MEM_WBReg_Stall[0]
        
        
    def step(self, instruction_set, memory):
        # step through the 5 stages of the pipeline
        
        self.IF_stage(instruction_set)
        self.ID_stage()
        self.EX_stage()
        self.Mem_stage(memory)
        self.WriteBack_stage(memory)
        print('\n\n', vars(self))
        
def main():
    # Clear the screen
    os.system('cls||clear')
    
    # Get instructions (Not part of memory)
    instructions = [0xa1020000,0x00000000,0x810AFFFC,0x00831820,0x01263820,0x01224820,
                       0x81180000,0x81510010,0x00624022,0x00000000,0x00000000,
                       0x00000000,0x00000000,0x8D48FFFC,0x00000000,0x00000000,
                       0x00000000,0x00000000,0x00000000,0x00000000];
    
    # Memory [Testing] where each address location can only store up to a byte 
    # (maximum value: 0xFF), currently needed for lB and SB
    memory  = [0]*0x400
    mem_value = 0x0
    for counter in range(len(memory)):
        memory[counter] = mem_value
        mem_value += 1
        if (mem_value % 0x100 == 0):
            mem_value = 0x0
    
    # Run instructions
    simulator = Pipeline_Simulator()
    
    for instruction in instructions:
        simulator.step(instructions, memory)
    
if __name__ == '__main__':
    main()
    
    