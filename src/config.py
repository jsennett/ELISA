######################################################################
# Memory
# 
# Specify memory levels and the memory heirarchy from bottom to top
######################################################################
from memory import Memory, Cache

DRAM = Memory(lines=2**8, delay=10, noisy=False, name="DRAM")
L2 = Cache(lines=32, words_per_line=4, delay=3, next_level=DRAM, noisy=False, name="L2")
L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=L2, top_level=True, noisy=False, name="L1")
memory_heirarchy = [L1, L2, DRAM]
