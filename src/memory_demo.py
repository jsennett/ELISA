"""

Josh Sennett
Yash Adhikari
CS 535

# TODO:
- make an interactive demo that supports:
    - read <address>
    - write <address>
    - display <all/cache/line>
- make a demo that reads assembly from a file
- add documentation + docstrings
"""


from memory import Memory, Cache, MemoryDemo, reset_cycle


def single_cache_demo():
    # Memory Demo
    instructions = []
    with open('instructions.txt', 'r') as file: 
        for line in file:
            tag = line.rstrip('\n')
            instructions.append(tag)
    

    DRAM = Memory(lines=2**8, delay=10, noisy=False)
    L1 = Cache(lines=8, words_per_line=2, delay=3, next_level=DRAM, top_level=True, noisy=False, associativity=2)
    demo = MemoryDemo(memory_heirarchy=[L1, DRAM])
    demo.execute(instructions)


def two_cache_demo():

    # Memory Demo
    instructions = []
    with open('instructions.txt', 'r') as file: 
        for line in file:
            tag = line.rstrip('\n')
            instructions.append(tag)

    DRAM = Memory(lines=2**8, delay=10, noisy=False)
    L2 = Cache(lines=8, words_per_line=4, delay=3, next_level=DRAM, noisy=False)
    L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=False)
    demo = MemoryDemo(memory_heirarchy=[L1, L2, DRAM])
    demo.execute(instructions)
    
def four_cache_demo():

    # Memory Demo
    instructions = []
    with open('instructions.txt', 'r') as file: 
        for line in file:
            tag = line.rstrip('\n')
            instructions.append(tag)

    DRAM = Memory(lines=2**32, delay=10, noisy=False)
    L4 = Cache(lines=64, words_per_line=4, delay=3, next_level=DRAM, noisy=False)
    L3 = Cache(lines=32, words_per_line=4, delay=3, next_level=L4, noisy=False)
    L2 = Cache(lines=16, words_per_line=4, delay=3, next_level=L3, noisy=False)
    L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=False)
    demo = MemoryDemo(memory_heirarchy=[L1, L2, DRAM])
    demo.execute(instructions)

if __name__ == '__main__':

    print("*" * 20 + " ONE LEVEL CACHE DEMO" + "*" * 20)
    single_cache_demo()
    print("*"*50)
    
    reset_cycle()
    
    print("*" * 20 + " TWO LEVEL CACHE DEMO" + "*" * 20)
    two_cache_demo()
    print("*"*50)
    
    reset_cycle()
    
    print("*" * 20 + " FOUR LEVEL CACHE DEMO" + "*" * 20)
    four_cache_demo()
    print("*"*50)
