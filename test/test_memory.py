import sys

sys.path.append("src/")
from memory import Memory, Cache
import logging
logging.basicConfig(level=logging.INFO)

def test_memory():

    # 3 level cache
    DRAM = Memory(lines=2**8, delay=10, noisy=False, name="DRAM")
    L3 = Cache(lines=2**5, words_per_line=4, delay=1, next_level=DRAM, noisy=False, name="L3")
    L2 = Cache(lines=2**5, words_per_line=4, delay=1, next_level=L3, noisy=False, name="L2")
    L1 = Cache(lines=8, words_per_line=4, delay=1, next_level=L2, noisy=False, name="L1")
    memory_heirarchy = [L1, L2, L3, DRAM]

    cycle = 0
    response = "wait"
    while response == "wait":
        response = memory_heirarchy[0].read(0)
        cycle += 1

    assert(cycle == 14)
