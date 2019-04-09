        .text
main:
    j alu_tester    

alu_tester:
    ########## ADDITION ###########
    # Store immediates so we can do some math
    addi $r1 $r0 1     # r1 = 1
    addi $r1 $r1 2     # r1 = r1 + 2
    add  $r1 $r1 $r1   # r1 = r1 + r1   
    lw $r2 expected_add 
    
    # If the branch is taken, something went wrong! 
    bne $r1 $r2 logic_tester  # r1 =? r2 

    ########## SUBTRACTION ###########
    addi $r3 $r0 100             # r3 = 100
    sub $r3 $r3 $r2              # r3 = r3 - r2
    lw $r4 expected_sub
    
    # If the branch is taken, something went wrong! 
    bne $r3 $r4 logic_tester     # r4 =? r1

    ########## ARITHMETIC SHIFT ###########
    addi $r5 $r0 0xABC0         # r5 = 0xABC0 (Negative!)
    sra $r5 $r5 4                   # r5 = $r5 >> 4
    lw $r6 expected_sra

    # If the branch is taken, something went wrong! 
    bne $r5 $r6 logic_tester        # r5 ?= r6
    
    ########## LOGICAL SHIFT & MULTIPLY ###########
    addi $r7 $r0 0x7FFF                 # r7 = 0x7FFF (Positive)
    sll $r8 $r7 8                   # r8 = r7 << 8 = 0x7FFF00
    mult $r7 $r8
    
    # Expected results: 0x3fff000100 
    # So, we expect: HI = 0x0000003f; LO = 0xff000100
    mfhi $r9
    lw $r10 expected_mult_hi
    bne $r9 $r10 logic_tester   # If HI was wrong, skip ahead!

    mflo $r11 hhh
    lw $r12 expected_mult_lo
    bne $r11 $r12 logic_tester  # If LO was wrong, skip ahead!

    ########## DIVIDE ###########
    addi $r13 $r0 17
    addi $r14 $r0 4
    div $r13 $r14

    # Expected results: 17 / 4 = 4 with remainder 1
    # So, we expect: HI = 1; LO = 4 
    mfhi $r16
    addi $r17 $r0 1

    mflo $r18 
    addi $r19 $r0 4

    # If the branch is taken, something went wrong! 
    bne $r16 $r17 logic_tester
    bne $r18 $r19 logic_tester

    # If all tests pass, increment the counter!
    jal correct 

logic_tester:
    ########## AND ###########
    addi $r20 $r0 0x00FF
    addi $r21 $r0 0x7F00
    
    # Expected: 0x00FF & 0x7F00 = 0
    and $r22 $r20 $r21
    bne $r22 $r0 load_n_store_tester

    ########## XORI  ###########
    # Expected: 0x00FF ^ 0x7F00 = 0x7FFF
    xori $r23 $r20 0x7F00   # r23 = 0x00FF ^ 0x7F00
    addi $r24 $r0 0x7FFF
    
    # If the branch is taken, something went wrong! 
    bne $r23 $r24 load_n_store_tester
    
    # If all tests pass, increment the counter!
    jal correct

load_n_store_tester:
    # Store some bytes in registers
    addi $r5 $r0 0xAB
    addi $r6 $r0 0xCD
    addi $r7 $r0 0xEF
    addi $r8 $r0 0x89

    # Set some offsets
    addi $r1 $r0 0
    addi $r2 $r0 1
    addi $r3 $r0 2
    addi $r4 $r0 3

    # Store the bytes in memory; line 256 is address 0x400
    sb $r5 256($r1)    # Address 0x1 + 0x400 = 0x400
    sb $r6 256($r2)    # Address 0x1 + 0x400 = 0x401
    sb $r7 256($r3)    # Address 0x1 + 0x400 = 0x402
    sb $r8 256($r4)    # Address 0x1 + 0x400 = 0x403

    # Load the word: we expect it to be 0x89EFCDAB,
    # since we are little endian
    lw $r25 256($r0)

    # Load expected value
    lw $r26 expected_lw

    # If the branch is taken, something went wrong! 
    bne $r25 $r26 floating_point_tester

    jal correct

floating_point_tester: 

    l.s $f0 one_x           # f0 = x
    add.s $f0 $f0 $f0     # f0 = f0 + f0
    l.s $f1 two_x           # f1 = 2x

    # Check if x + x == 2x
    c.eq.s $f0 $f1

    # If the branch is taken, something went wrong! 
    bc1f exit
    
    jal correct

exit:
    # Syscall to exit.
    syscall

correct:
    addi $r30 $r30 1
    jr $ra

.data
    expected_add: 6
    expected_sub: 94
    expected_sra: 0xFFFFFABC
    expected_mult_hi: 0x0000003f
    expected_mult_lo: 0xff000100
    expected_lw: 0x89EFCDAB
    one_x: 2.5
    two_x: 5.0
