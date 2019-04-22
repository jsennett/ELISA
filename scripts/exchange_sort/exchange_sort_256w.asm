        .text
main:

    # load length value and array address
    #     r1 = passes remaining
    #     r2 = iterations remaining in current pass
    #     r3 = address of left element to compare;
    #          the adjacent right element is 1(r3)
    lw $r1 length
    lw $r2 length
    la $r3 array

loop:
    beq $r1 $zero exit      # If no swaps occured, the array is sorted.
    addi $r1 $r1 -1    # Decrement counter
    addi $r2 $r2 -1    # Decrement counter
    blez $r2 reset     # Once a pass is complete, reset to start
    
    lw $r4 0($r3)      # load left
    lw $r5 1($r3)      # load right

    slt $r6 $r5 $r4        # check if swap needed
    bgtz $r6 yes_swap   # if swap needed, branch
    beq $r4 $r5 no_swap    # if left > right, swap
    addi $r3 $r3 4         # Increment position by 0x4
    j loop

yes_swap:
    sw $r5 0($r3)          # place right word left
    sw $r4 1($r3)          # place left word right
    addi $r3 $r3 4         # increment array position
    lw $r1 length  # $r1 back to length
    j loop 

no_swap:
    addi $r3 $r3 4
    j loop
    
exit:
    syscall
    syscall
    syscall

reset: 
    la $r3 array  # reset to start of word
    lw $r2 length         # Reset counter to word length
    j loop

.data
    array: [230, 41, 177, 105, 45, 216, 253, 9, 53, 183, 147, 79, 203, 80, 129, 54, 132, 41, 124, 179, 30, 193, 199, 210, 17, 232, 19, 208, 147, 135, 96, 111, 155, 212, 214, 98, 16, 122, 75, 230, 86, 182, 55, 208, 130, 67, 81, 198, 236, 44, 85, 152, 34, 254, 93, 126, 160, 211, 186, 238, 249, 71, 82, 154, 121, 154, 246, 41, 4, 21, 85, 26, 102, 1, 12, 151, 131, 73, 160, 197, 215, 92, 217, 148, 230, 226, 54, 98, 158, 207, 219, 72, 85, 38, 247, 119, 236, 215, 12, 119, 40, 45, 234, 90, 213, 170, 96, 135, 226, 119, 37, 230, 149, 95, 28, 166, 33, 171, 66, 63, 135, 115, 198, 254, 26, 127, 174, 201, 140, 64, 163, 221, 103, 58, 57, 251, 242, 15, 221, 84, 15, 228, 183, 179, 162, 50, 187, 203, 219, 48, 28, 245, 137, 110, 127, 16, 57, 212, 53, 195, 59, 97, 137, 222, 126, 174, 239, 182, 53, 107, 121, 19, 155, 152, 79, 142, 17, 116, 231, 27, 169, 248, 43, 59, 174, 146, 19, 117, 233, 5, 104, 107, 63, 22, 65, 151, 142, 185, 31, 29, 39, 52, 120, 62, 65, 245, 10, 77, 65, 22, 114, 201, 125, 70, 247, 123, 14, 254, 96, 217, 211, 23, 136, 142, 67, 208, 128, 39, 66, 85, 217, 239, 243, 5, 154, 228, 64, 71, 38, 255, 83, 220, 199, 23, 43, 28, 44, 163, 130, 241, 66, 248, 179, 15, 51, 249]
    length: 256
