import sys

sys.path.append("src/")
from simulator import Simulator
from assembler import assemble_to_numerical
from memory import Memory, Cache

def test_IF():

    # Create a simulator
    sim = Simulator()

     # Set Memory
    DRAM = Memory(lines=2**12, delay=10)
    L2 = Cache(lines=32, words_per_line=4, delay=1, associativity=1, next_level=DRAM, name="L2")
    L1 = Cache(lines=8, words_per_line=4, delay=0, associativity=1, next_level=L2, name="L1")
    sim.memory_heirarchy = [L1, L2, DRAM]

    # Set initial register values for debugging
    sim.R = list(range(0, 32))

    # Load some instructions
    with open('test/IF_test.asm') as f:
        file_contents = f.read()

    instructions = assemble_to_numerical(file_contents)
    sim.set_instructions(instructions)

    # Step a few times; it will take 10 + 1 + 1 steps to load the first instruction
    for i in range(12):
        assert(sim.buffer == [sim.IF_NOOP, sim.ID_NOOP, sim.EX_NOOP, sim.MEM_NOOP])
        sim.step()


    # After the initial compulsory miss, with four words per line,
    # our first four fetches should now be cache hits.
    # Ensure that the first buffer contains the next instruction after each step
    for i in range(4):
        assert(sim.buffer[0] == [instructions[i], (i + 1) * 4])
        sim.step()

    # $r4 has initial value of 4. After LW completes, it should have value 0
    # This should take 10 cycles to load the next block of instructions,
    # then five cycles for the instruction to go through the pipeline
    # and 11 delay cycles to load the word from memory
    print(sim.memory_heirarchy[0].data)
    for i in range(10 + 5 + 11):
        assert(sim.R[4] == 4)
        sim.step()

    # Now, the instruction should have been written back, replacing 104 with 0.
    assert(sim.R[4] == 0)
