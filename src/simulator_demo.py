"""

Josh Sennett
Yash Adhikari
CS 535

Simulator Demo

# Requirements:

Partial Simulator: This first version of the simulation fetches instructions from memory
and passes them through a pipeline consisting of at least five stages (fetch, decode,
execute, memory, write back), with no forwarding or interrupt handling. It keeps and
displays a count of simulated clock cycles. It should have a user interface (UI) that
enables the user to observe the state of the architecture as a program executes. Thus,
somewhat like a debugger, it will allow single stepping, execution to a breakpoint, and/or
for a specified number of cycles. It will need commands for loading and saving
programs (or the entire state), and resetting the state.

- fetch
- decode
- execute
- memory
- write back

Instructions will be encoded in binary (do not use strings for this). At a later stage, you
will implement a simple assembler/disassembler so that you can write code and see it in
memory in a more meaningful form. Note that the architecture has only one memory,
which contains both instructions and data, all represented in binary. Because the
memory will be too large to be displayed on the screen all at once, you will need a UI
that can selectively display sections of it.

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

# Stages:
# - fetch
# - decode
# - execute
# - memory
# - write back

class Simulator:


    def __init__():
        self.pipeline = []

    def step_forward():

        """
        write_back:

            take value at pipeline[4]:
                if None/stall/wait - dont do anything
            else:
                update registers based on value 

        memory:
            take value at pipeline[3]:
                do something
                delay some cycles
                write the results to pipeline[4] (location, value)  

        execute:
            take value at pipeline[2]:
                do something
                delay some cycles
                write results to pipeline[3]

        decode:
            etc.

        fetch:
            etc.

        """



