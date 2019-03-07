"""

Josh Sennett
Yash Adhikari
CS 535

User Interface

# Requirements:

GUI:
enables the user to observe the state of the architecture as a program executes. Thus,
somewhat like a debugger, it will allow single stepping, execution to a breakpoint, and/or
for a specified number of cycles. It will need commands for loading and saving
programs (or the entire state), and resetting the state.

The user interface will need to be extended to
support running to completion, breakpoints, viewing memory in different formats
(instruction, decimal, hex, etc.), and managing the configurations of the simulator. 

Display clock cycles

For the demonstration, you just need to have enough instructions working to show that
all of the major operation types (load, store, ALU, branch) are working. The simulator
should be able to load a binary program, and then single-step execute it. The program
must at least demonstrate loading and storing values between memory and registers,
register-to-register arithmetic, and a conditional branch. A good demonstration is the
equivalent of a for loop that reads a series of pairs of values from memory, adds them,
stores the results back to memory, and exits when the loop control counter reaches the
termination condition.

The simulator should keep and display a count of the execution cycles, and it should be
possible to run both with and without a cache, and in a mode where the pipeline is
disabled (each instruction goes all the way through before the next one starts).
The user interface at this stage should support viewing the registers (including PC,
status, etc.) and memory (main and cache) in hexadecimal, loading a program from a
file, and stepping through it to see how the state changes. At this point, you will have all
of the major components of the simulator working.
"""

