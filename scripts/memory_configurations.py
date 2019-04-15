import sys
sys.path.append("src/")

from memory import Memory, Cache

# m1: Main memory
DRAM = Memory(lines=2**12, delay=100)
m1 = [DRAM]

# m2: Memory + direct mapped L1 caching, 4 words per line
DRAM = Memory(lines=2**12, delay=100)
L1 = Cache(lines=256, words_per_line=4, delay=0, associativity=1, next_level=DRAM)
m2 = [L1, DRAM]

# m2: Memory + direct mapped L1, L2 caching, 4 words per line
DRAM = Memory(lines=2**12, delay=100)
L2 = Cache(lines=512, words_per_line=4, delay=0, associativity=1, next_level=DRAM)
L1 = Cache(lines=256, words_per_line=4, delay=0, associativity=1, next_level=DRAM)
m3 = [L1, DRAM]
