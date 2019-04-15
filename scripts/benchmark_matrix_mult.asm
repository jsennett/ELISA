# The following file will test the matrix multiplication benchmark
# We will be storing the matrix as a vector into main memory and loading in 
# value from matrix 1 into reegister 1 and value of matrix 2 into register 2.
# We will perform a multiplication operation on these two registers and store 
# the value in register 3. The last part of this matrix multiplication is to
# increment the value of register 4 by the value in register 3. 
#   Matrix: 1 [m by k], matrix 2: [k by n]
#   Loop r through m times
#       Loop c through n times
#           Loop i through k times
#               multiply value from matrix 1 at index (r-1) * m by value from matrix 2 at index (i-1) * n
#               there may be an offset in memory due to loading of instructions
#               use this value to increment the value in register 19
#               Place this value in a new matrix at index (r-1) * n + some offset
#               set the value of register 19 baak to 0

# Load data in memory location starting at X to X+m*k
# Load another set of data in memory location starting at X+m*k to (X+m*k) + k*n
# Perform matrix multiplication
# Store data in memory location X+m*k+k*n to (X+m*k+k*n) + m*n
####################### Start of Assembly #######################

        .text
main:
    
    # clear register values that will store counters to 1
    addi $r1 $r0 1                          # Store r
    addi $r2 $r0 1                          # Store c
    addi $r3 $r0 1                          # Store i
    
    add $r19 $r0 $r0                        # Store 0 into $r19 - used for final value
    
    # store matrix sizes in registers
    lw $r4 row_m                            # Store value of m+1 (constant)
    lw $r5 col_n                            # Store value of n+1 (constant)
    lw $r6 k                                # Store value of k+1 (constant)
    
    lw $r11 starting_X                      # Store starting point of data X (constant)
    lw $r12 address_factor                  # Store factor to get address (constant)
    
    addi $r7 $r4 -1                         # Store value of m
    addi $r8 $r5 -1                         # Store value of n
    addi $r9 $r6 -1                         # Store value of k
    
    mult $r7 $r9                            # m * k
    mflo $r15                               # $r15 = m * k
    add $r15 $r11 $r15                      # $r15 = X + (m * k) (constant)
    
    mult $r8 $r9                            # n * k
    mflo $r20                               # $r20 = n * k
    add $r20 $r15 $r20                      # $r20 = (X+(m*k)) + n * k (constant)
    
    
    # load data of Matrix 1 into main memory
    addi $r25 $r11 0                        # add starting mem address
    addi $r26 $r0 0                         # value
    
loop_data1:
    addi $r25 $r25 1                        # increment by 1
    addi $r26 $r26 1                        # increment by 1
    mult $r25 $r12                          # multiply by 4 to properly index
    mflo $r29                               # $r29 = address
    sw $r26 0($r29)                         # ADDRESS at $r29 = value from $r26
    bne $r25 $r15, loop_data1
    
    # Load data of Matrix 2 into main memory
    addi $r27 $r15 0                        # add starting mem address
    addi $r28 $r0 13                        # value
loop_data2:
    addi $r27 $r27 1                        # increment by 1
    addi $r28 $r28 -1                       # decrement by 1
    mult $r27 $r12                          # multiply by 4 to properly index
    mflo $r30                               # $r30 = address
    sw $r28 0($r30)                         # ADDRESS at $r30 = value from $r28
    bne $r27 $r20, loop_data2
    
    
# perform matrix multiplication
# loop through m rows in matrix 1
loop_r:

# loop through n columns in matrix 2
loop_c:

# loop through k times to perform multiplication / addition (main calculation)
loop_i:
    
    # Get value from matrix 1 by finding the proper index
    addi $r22 $r1 -1
    
    mult $r22 $r7                           # (r-1) * m
    mflo $r13                               # $r13 = (r-1) * m
    add $r13 $r13 $r3                       # add counter i
    add $r13 $r13 $r11                      # add starting mem address
    mult $r13 $r12                          # multiply by 4 to properly index
    mflo $r13                               # $r13 = address
    lw $r14 0($r13)                         # $r14 = value from matrix 1
    
    # Get value from matrix 2 by finding the proper index
    addi $r10 $r3 -1
    mult $r10 $r8                           # (i-1) * n
    mflo $r16                               # $r16 = (i-1) * n
    add $r16 $r16 $r2                       # $r16 += c (proper relative index)
    
    add $r16 $r16 $r15                      # add starting mem address
    mult $r16 $r12                          # multiply by 4 to properly index
    mflo $r16                               # $r16 = address
    lw $r17 0($r16)                         # $r17 = value from matrix 2
    
    # multiply the two values from the matrices and increment the final value
    mult $r14 $r17
    mflo $r18
    add $r19 $r19 $r18
    
    
    # loop back to loop_i
    addi $r3 $r3 1
    bne $r3 $r6, loop_i
    addi $r3 $r0 1
    
    # Store value into matrix 3 by finding the proper index
    
    mult $r22 $r8                           # (r-1) * n
    mflo $r21                               # $r21 = (r-1) * n
    add $r21 $r21 $r2                       # $r21 += c
    
    add $r21 $r21 $r20                      # add starting mem address
    mult $r21 $r12                          # multiply by 4 to properly index
    mflo $r21                               # $r21 = address
    sw $r19 0($r21)                         # store value of calculation into matrix 3
    add $r19 $r0 $r0                        # restore $r19 to 0 - used for final value


    # loop back to loop_c   
    addi $r2 $r2 1
    bne $r2 $r5, loop_c
    addi $r2 $r0 1


    # loop back to loop_r    
    addi $r1 $r1 1
    bne $r1 $r4, loop_r
    addi $r1 $r0 1

exit:
    # Syscall to exit.
    syscall
    syscall
    syscall

# Matrix 1 of shape 3x3 and value
# [1 2 3]
# [4 5 6]
# [7 8 9]

# Matrix 2 of shape 3x4 and value
# [12 11 10 9]
# [8  7  6  5]
# [4  3  2  1]

.data
    starting_X: 100
    
    # must be 1 more than actual number to handle loop condition
    row_m: 4
    k: 4
    col_n: 5
    
    address_factor: 4