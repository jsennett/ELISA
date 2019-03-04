######################################################################
# Memory
# 
# Specify memory levels and the memory heirarchy from bottom to top
######################################################################
from memory import Memory, Cache

# Interactive demo - no assembly file specified.
# python3 src/memory_demo.py
DRAM = Memory(lines=2**8, delay=10, noisy=True, name="DRAM")
L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=DRAM, top_level=True, noisy=True, name="L1")
memory_heirarchy = [L1, L2, DRAM]

######################################################################

# # Interactive demo - no assembly file specified.
# # python3 src/memory_demo.py test/memory_demo.asm

# DRAM = Memory(lines=2**8, delay=10, noisy=False, name="DRAM")
# L3 = Cache(lines=2**5, words_per_line=4, delay=3, next_level=DRAM, noisy=False, name="L3")
# L2 = Cache(lines=2**5, words_per_line=4, delay=3, next_level=L2, noisy=False, name="L2")
# L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L1, top_level=True, noisy=False, name="L1")
# memory_heirarchy = [L1, L2, L3, DRAM]

######################################################################


# # One-level cache
# DRAM = Memory(lines=2**8, delay=10, noisy=False)
# L1 = Cache(lines=8, words_per_line=2, delay=3, next_level=DRAM, top_level=True, noisy=False, associativity=2)
# memory_heirarchy = [L1, DRAM]

# # Two-level cache
# DRAM = Memory(lines=2**8, delay=10, noisy=False)
# L2 = Cache(lines=8, words_per_line=4, delay=3, next_level=DRAM, noisy=False)
# L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=False)
# memory_heirarchy = [L1, L2, DRAM]

# # Four-level cache
# DRAM = Memory(lines=2**32, delay=10, noisy=False)
# L4 = Cache(lines=64, words_per_line=4, delay=3, next_level=DRAM, noisy=False)
# L3 = Cache(lines=32, words_per_line=4, delay=3, next_level=L4, noisy=False)
# L2 = Cache(lines=16, words_per_line=4, delay=3, next_level=L3, noisy=False)
# L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=False)
# 