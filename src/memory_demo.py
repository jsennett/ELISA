"""

Josh Sennett
Yash Adhikari
CS 535

# TODO:
- add documentation + docstrings
- test memory hit/miss rate for different cache/associativity configurations
"""
from memory import MemoryDemo, reset_metrics
import config
import sys
import os

def main():

    # Clear the screen
    os.system('cls||clear')

    # Get command line arguments
    args = sys.argv

    # Interactive mode: no assembly file specified    
    demo = MemoryDemo(memory_heirarchy=config.memory_heirarchy)

    # Interactive mode - no file specified
    if len(args) == 1:
        demo.execute_instructions(filename=None)

    # File specified - run through all instructions
    elif len(args) == 2:
        demo.execute_instructions(filename=args[1])
    else:
        print("Usage: python3 src/memory_demo.py [ASSEMBLY_FILEPATH]")
        sys.exit(0)

if __name__ == '__main__':
    main()