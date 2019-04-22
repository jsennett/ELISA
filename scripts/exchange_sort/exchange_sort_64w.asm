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
    array: [25, 14, 46, 31, 47, 51, 21, 6, 51, 45, 41, 26, 0, 20, 51, 4, 58, 5, 18, 14, 53, 12, 27, 38, 39, 9, 10, 43, 57, 21, 58, 58, 59, 47, 7, 22, 41, 23, 27, 9, 13, 16, 49, 59, 21, 21, 28, 48, 14, 3, 50, 61, 54, 5, 42, 51, 43, 37, 11, 10, 14, 30, 39, 58]
    length: 64
