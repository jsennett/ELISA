add $r1 $r2 $r3
addi $r4 $r8 0x123
sub $r1 $r2 $r3
sll $r5 $r6 0x12
srl $r5 $r6 0x12
mult $r3 $r4
div $r3 $r4
and $r1 $r2 $r3
andi $r1 $r2 0x01
or $r1 $r2 $r3
ori $r1 $r2 0x04
xor $r1 $r2 $r4
xori $r1 $r2 0x04
nor $r1 $r2 $r4
beq $r1 $r2 0x1234
bne $r1 $r2 0x1234
bgez $r1 0x1234
blez $r1 0x1234
bgtz $r2 0x4567
bltz $r2 0x4567
j 0x3456
jal 0x3456
jr $r3
slt $r1 $r2 $r3
slti $r1 $r2 0x1234
lw $r1 0x04($r3)
sw $r1 0x04($r3)