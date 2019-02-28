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
    instructions = [
        "load 0b00000000",                  # 13
        "load 0b00000000",                  # 3
        "load 0b00000000",                  # 3
        "store 0b01101011 0b00000001",      # 10
        "load 0b01101011",                  # 13
        "store 0b01101011 0b00000001"       # 13
    ]

    DRAM = Memory(lines=2**8, delay=10, noisy=True)
    L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=DRAM, top_level=True, noisy=True)
    demo = MemoryDemo(memory_heirarchy=[L1, DRAM])
    demo.execute(instructions)


def two_cache_demo():

    # Memory Demo
    instructions = [
        "load 0b00000000",                  # 13
        "load 0b00000000",                  # 3
        "load 0b00000000",                  # 3
        "store 0b01101011 0b00000001",      # 10
        "load 0b01101011",                  # 13
        "store 0b01101011 0b00000001"       # 13
    ]

    DRAM = Memory(lines=2**8, delay=10, noisy=True)
    L2 = Cache(lines=8, words_per_line=4, delay=3, next_level=DRAM, noisy=True)
    L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=True)
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

