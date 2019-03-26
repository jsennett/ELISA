# $r2 = i
# registers have default values 

main:
    lw $r2 0($r31)           # i=0

loop:
    add $r2 $r2 $r1          # r2 = r2 + 1
    bne $r2 $r10, loop       # exit if r2 == r10 (if i == 10)
exit:
    sw $r2 100($r0)          # store x to 0x190

