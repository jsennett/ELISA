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
#               multiple value from matrix 1 at index r*iby value from matrix 2 at index c*i
#               there may be an offset in memory due to loading of instructions
#               use this value to increment the value in register 4
#               Place this value in a new matrix at index r*c + some offset
#               set the value of register 4 to 0

# Load data in memory location starting at X to X+m*k
# Load another set of data in memory location starting at X+m*k to (X+m*k) + k*n
# Perform matrix multiplication
# Store data in memory location X+m*k+k*n to (X+m*k+k*n) + m*n
