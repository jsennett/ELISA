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

# Interactive demo - no assembly file specified.
# python3 src/memory_demo.py test/memory_demo.asm
"""
DRAM = Memory(lines=2**8, delay=10, noisy=False, name="DRAM")
L3 = Cache(lines=2**5, words_per_line=4, delay=3, next_level=DRAM, noisy=False, name="L3")
L2 = Cache(lines=2**5, words_per_line=4, delay=3, next_level=L2, noisy=False, name="L2")
L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L1, top_level=True, noisy=False, name="L1")
memory_heirarchy = [L1, L2, L3, DRAM]
"""