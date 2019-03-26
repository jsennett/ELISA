import sys

sys.path.append("src/")
from simulator import Simulator
from assembler import assemble_to_numerical

def test_IF():

    # Create a simulator
    sim = Simulator()

    # Load some instructions
    with open('test/simulator_test.asm') as f:
        file_contents = f.read()

    instructions = assemble_to_numerical(file_contents)
    sim.set_instructions(instructions)

    # Step a few times
    assert(sim.buffer == [0, 0, 0, 0])

    # Check pipeline values after each step for a few steps.
    sim.step()
    assert(sim.buffer == [0, 0, 0, 0])
