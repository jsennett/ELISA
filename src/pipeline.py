# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:06:58 2019

@author: ayash
"""
from memory import Memory, Cache
import os

class Pipeline_Simulator:
    
    def __init__(self):
        self.register = [0xff] * 32             # 32 registers pre-defined        
        
        self.IF_IDReg_IncrPC = [0] * 2
        self.IF_IDReg_Inst = [0] * 2

        self.ID_EXReg_IncrPC = [0] * 2
        self.ID_EXReg_ReadReg1Value = [0] * 2
        self.ID_EXReg_ReadReg2Value = [0] * 2
        self.ID_EXReg_SEOffset = [0] * 2
        self.ID_EXReg_WriteReg_20_16 = [0] * 2
        self.ID_EXReg_WriteReg_15_11 = [0] * 2
        self.ID_EXReg_Function = [0] * 2
        self.ID_EXReg_RegDst = [0] * 2
        self.ID_EXReg_ALUSrc = [0] * 2
        self.ID_EXReg_ALUOp1 = [0] * 2
        self.ID_EXReg_ALUOp2 = [0] * 2
        self.ID_EXReg_MemRead = [0] * 2
        self.ID_EXReg_MemWrite = [0] * 2
        self.ID_EXReg_MemToReg = [0] * 2
        self.ID_EXReg_RegWrite = [0] * 2

        self.EX_MEMReg_Zero = [0] * 2
        self.EX_MEMReg_ALUResult = [0] * 2
        self.EX_MEMReg_SWValue = [0] * 2
        self.EX_MEMReg_WriteRegNum = [0] * 2
        self.EX_MEMReg_MemRead = [0] * 2
        self.EX_MEMReg_MemWrite = [0] * 2
        self.EX_MEMReg_MemToReg = [0] * 2
        self.EX_MEMReg_RegWrite = [0] * 2

        self.MEM_WBReg_LWDataValue = [0] * 2
        self.MEM_WBReg_ALUResult = [0] * 2
        self.MEM_WBReg_WriteRegNum = [0] * 2
        self.MEM_WBReg_MemToReg = [0] * 2
        self.MEM_WBReg_RegWrite = [0] * 2
        
        
        
    
    def IF_stage(self, instruction_set):
        
        self.IF_IDReg_Inst[0] = instruction_set[self.IF_IDReg_IncrPC[0]//4]
        self.IF_IDReg_IncrPC[0] += 4 
        
    def ID_stage(self):
        opcode = (self.instruction & 0xFC000000) >> 26
        srcRegister = (self.instruction & 0x03E00000) >> 21
        srcOrDestRegister = (self.instruction & 0x001F0000) >> 16
        destRegister = (self.instruction & 0x0000F800) >> 11
        
        self.ID_EXReg_IncrPC[0] = self.IF_IDReg_IncrPC[1]
        self.ID_EXReg_ReadReg1Value[0] = self.register[srcRegister]
        self.ID_EXReg_ReadReg2Value[0] = self.register[srcOrDestRegister]
        self.ID_EXReg_WriteReg_20_16[0] = srcOrDestRegister
        self.ID_EXReg_WriteReg_15_11[0] = destRegister
        
        if (opcode == 0):
            # This is the R-Format
            function = (self.IF_IDReg_Inst[1] & 0x0000003F)
            # Use given format
            if (function == 0x20):
                # addition
                self.ID_EXReg_SEOffset[0] = 0
                self.ID_EXReg_Function[0] = 0x20
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
                self.ID_EXReg_Function[0] = 0x22
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
                self.ID_EXReg_Function[0] = 0
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
            # This is the I-Format or J-format
            offset = (self.IF_IDReg_Inst[1] & 0x0000FFFF)
            # use given format
            if (opcode == 0x20):
                # lb
                self.ID_EXReg_SEOffset[0] = offset
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
                self.ID_EXReg_SEOffset[0] = offset
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
                # do nothing
                pass
        
        
    def EX_stage(self):
        
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
            # Subtraction
            self.EX_MEMReg_Zero[0] = 0xf
            self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + (self.ID_EXReg_ReadReg2Value[1] + 1)
            self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
            self.EX_MEMReg_WriteRegNum[0] = self.ID_EXReg_WriteReg_15_11[1]

            self.EX_MEMReg_MemRead[0] = 0
            self.EX_MEMReg_MemWrite[0] = 0
            self.EX_MEMReg_MemToReg[0] = 0
            self.EX_MEMReg_RegWrite[0] = 1
            
        elif (self.ID_EXReg_Function[1] == 0x0 and self.ID_EXReg_MemWrite[1] == 0 and self.ID_EXReg_MemToReg[1] == 1):
            # LB
            self.EX_MEMReg_Zero[0] = 0xf
            self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_SEOffset[1]
            self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
            self.EX_MEMReg_WriteRegNum[0] = self.ID_EXReg_WriteReg_20_16[1]

            self.EX_MEMReg_MemRead[0] = 1
            self.EX_MEMReg_MemWrite[0] = 0
            self.EX_MEMReg_MemToReg[0] = 1
            self.EX_MEMReg_RegWrite[0] = 1
            
        elif (self.ID_EXReg_Function[1] == 0x0 and self.ID_EXReg_MemWrite[1] == 1):
            # SB
            self.EX_MEMReg_Zero[0] = 0xf;
            self.EX_MEMReg_ALUResult[0] = self.ID_EXReg_ReadReg1Value[1] + self.ID_EXReg_SEOffset[1]
            self.EX_MEMReg_SWValue[0] = self.ID_EXReg_ReadReg2Value[1]
            self.EX_MEMReg_WriteRegNum[0] = 0

            self.EX_MEMReg_MemRead[0] = 0
            self.EX_MEMReg_MemWrite[0] = 1
            self.EX_MEMReg_MemToReg[0] = 0
            self.EX_MEMReg_RegWrite[0] = 0
            
        else:
            #NoOP
            self.EX_MEMReg_MemRead[0] = 0
            self.EX_MEMReg_MemWrite[0] = 0
            self.EX_MEMReg_MemToReg[0] = 0
            self.EX_MEMReg_RegWrite[0] = 0
            
    def Mem_stage(self, Main_Mem):
        
        # index into main memory if instruction is an lb. For everything else, pass the data along in the pipeline
        self.MEM_WBReg_ALUResult[0] = self.EX_MEMReg_ALUResult[1]
        self.MEM_WBReg_WriteRegNum[0] = self.EX_MEMReg_WriteRegNum[1]
        self.MEM_WBReg_MemToReg[0] = self.EX_MEMReg_MemToReg[1]
        self.MEM_WBReg_RegWrite[0] = self.EX_MEMReg_RegWrite[1]
        if (self.EX_MEMReg_MemWrite[1] == 1 and self.EX_MEMReg_RegWrite[1] == 1):
            # handle lb
            self.MEM_WBReg_LWDataValue[0] = Main_Mem[(self.EX_MEMReg_ALUResult[1])]
        elif (self.EX_MEMReg_MemWrite[1] == 0 and self.EX_MEMReg_RegWrite[1] == 0):
            # Noop do nothing
            pass
        else:
            # other instructions?
            # handle other instructions
            self.MEM_WBReg_LWDataValue[0] = 0
            if (self.EX_MEMReg_RegWrite[1] == 0):
                # write back to main memory
                Main_Mem[(self.EX_MEMReg_ALUResult[1])] = self.EX_MEMReg_SWValue[1]
        
    def WriteBack_stage(self, Main_Mem):
        # write back to registers
        if(self.MEM_WBReg_RegWrite[1] == 1 and self.MEM_WBReg_MemToReg[1] == 0):
            self.register[self.MEM_WBReg_WriteRegNum[1]] = self.MEM_WBReg_ALUResult[1]
        elif(self.MEM_WBReg_RegWrite[1] == 1 and self.MEM_WBReg_MemToReg[1] == 1):
            print(self.MEM_WBReg_WriteRegNum, self.MEM_WBReg_ALUResult)
            self.register[self.MEM_WBReg_WriteRegNum[1]] = Main_Mem[self.MEM_WBReg_ALUResult[1]]
        else:
            # no registers are written to in case of a noop or a sb
            pass
            
    def Copy_write_to_read(self):
        self.IF_IDReg_IncrPC[1] = self.IF_IDReg_IncrPC[0]
        self.IF_IDReg_Inst[1] = self.IF_IDReg_Inst[0]

        self.ID_EXReg_IncrPC[1] = self.ID_EXReg_IncrPC[0]
        self.ID_EXReg_ReadReg1Value[1] = self.ID_EXReg_ReadReg1Value[0]
        self.ID_EXReg_ReadReg2Value[1] = self.ID_EXReg_ReadReg2Value[0]
        self.ID_EXReg_SEOffset[1] = self.ID_EXReg_SEOffset[0]
        self.ID_EXReg_WriteReg_20_16[1] = self.ID_EXReg_WriteReg_20_16[0]
        self.ID_EXReg_WriteReg_15_11[1] = self.ID_EXReg_WriteReg_15_11[0]
        self.ID_EXReg_Function[1] = self.ID_EXReg_Function[0]
        self.ID_EXReg_RegDst[1] = self.ID_EXReg_RegDst[0]
        self.ID_EXReg_ALUSrc[1] = self.ID_EXReg_ALUSrc[0]
        self.ID_EXReg_ALUOp1[1] = self.ID_EXReg_ALUOp1[0]
        self.ID_EXReg_ALUOp2[1] = self.ID_EXReg_ALUOp2[0]
        self.ID_EXReg_MemRead[1] = self.ID_EXReg_MemRead[0]
        self.ID_EXReg_MemWrite[1] = self.ID_EXReg_MemWrite[0]
        self.ID_EXReg_MemToReg[1] = self.ID_EXReg_MemToReg[0]
        self.ID_EXReg_RegWrite[1] = self.ID_EXReg_RegWrite[0]

        self.EX_MEMReg_Zero[1] = self.EX_MEMReg_Zero[0]
        self.EX_MEMReg_ALUResult[1] = self.EX_MEMReg_ALUResult[0]
        self.EX_MEMReg_SWValue[1] = self.EX_MEMReg_SWValue[0]
        self.EX_MEMReg_WriteRegNum[1] = self.EX_MEMReg_WriteRegNum[0]
        self.EX_MEMReg_MemRead[1] = self.EX_MEMReg_MemRead[0]
        self.EX_MEMReg_MemWrite[1] = self.EX_MEMReg_MemWrite[0]
        self.EX_MEMReg_MemToReg[1] = self.EX_MEMReg_MemToReg[0]
        self.EX_MEMReg_RegWrite[1] = self.EX_MEMReg_RegWrite[0]

        self.MEM_WBReg_LWDataValue[1] = self.MEM_WBReg_LWDataValue[0]
        self.MEM_WBReg_ALUResult[1] = self.MEM_WBReg_ALUResult[0]
        self.MEM_WBReg_WriteRegNum[1] = self.MEM_WBReg_WriteRegNum[0]
        self.MEM_WBReg_MemToReg[1] = self.MEM_WBReg_MemToReg[0]
        self.MEM_WBReg_RegWrite[1] = self.MEM_WBReg_RegWrite[0]
        
def main():
    # Clear the screen
    os.system('cls||clear')
    
    # Get instructions
    instruction_new = [0xa1020000,0x810AFFFC,0x00831820,0x01263820,0x01224820,
                       0x81180000,0x81510010,0x00624022,0x00000000,0x00000000,
                       0x00000000,0x00000000];
    
    # Set memory and registers [Actual]
    DRAM = Memory(lines=2**8, delay=10, noisy=False, name="DRAM")
    L3 = Cache(lines=2**5, words_per_line=4, delay=3, next_level=DRAM, noisy=False, name="L3")
    L2 = Cache(lines=2**5, words_per_line=4, delay=3, next_level=L3, noisy=False, name="L2")
    L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=False, name="L1")
    memory_heirarchy = [L1, L2, L3, DRAM]
    
    # Memory [Testing] where each address location can only store up to a byte 0xFF
    memory  = [0]*0x400
    mem_value = 0x0
    for counter in range(len(memory)):
        memory[counter] = mem_value
        mem_value += 1
        if (mem_value % 0x100 == 0):
            mem_value = 0x0
    
    # Run instructions
    simulator = Pipeline_Simulator()
    
    for instruction in instruction_new:
            simulator.IF_stage(instruction_new)
            simulator.ID_stage()
            simulator.EX_stage()
            simulator.Mem_stage(memory)
            simulator.WriteBack_stage(memory)
            print('\n\n', vars(simulator))
            simulator.Copy_write_to_read()
    
if __name__ == '__main__':
    main()
    
    