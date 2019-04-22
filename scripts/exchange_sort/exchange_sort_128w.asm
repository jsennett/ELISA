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
    array: [40, 69, 99, 117, 87, 19, 73, 56, 79, 53, 59, 82, 34, 107, 106, 12, 108, 95, 52, 49, 50, 6, 117, 101, 99, 117, 125, 68, 28, 32, 24, 50, 11, 51, 73, 25, 80, 95, 58, 15, 96, 12, 43, 102, 31, 17, 108, 20, 105, 102, 23, 46, 5, 18, 127, 26, 54, 21, 40, 83, 108, 78, 113, 75, 76, 25, 51, 116, 77, 91, 14, 24, 65, 54, 39, 71, 30, 103, 120, 91, 49, 80, 17, 38, 83, 5, 50, 47, 5, 118, 19, 84, 31, 108, 19, 70, 27, 68, 55, 4, 15, 61, 7, 89, 51, 36, 108, 78, 44, 98, 104, 68, 12, 5, 40, 84, 81, 39, 29, 56, 28, 96, 104, 82, 56, 29, 100, 114]
    length: 128
