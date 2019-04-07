import sys

sys.path.append("src/")
from memory import Memory, Cache
import logging
logging.basicConfig(level=logging.INFO)


def test_memory_read_word():
    mem = Memory(lines=2**8, delay=0)
    mem.data = list(range(2**8))
    assert(mem.read(0x1)[0] == 0)

def test_memory_write_word():
    mem = Memory(lines=2**8, delay=0)
    mem.write(0x0, 1)
    assert(mem.data[0] == 1)

def test_memory_read_byte():
    mem = Memory(lines=2**15, delay=0)
    mem.data = list(range(2**15))

    # address 0xbb3c has value 11983 = 0x2ECF
    assert(mem.read(0xbb3c)[0] == 0x2ECF)
    assert(mem.read(0xbb3c, only_byte=True)[0] == 0xCF)
    assert(mem.read(0xbb3c + 1, only_byte=True)[0] == 0x2E)

def test_memory_write_byte():
    mem = Memory(lines=2**8, delay=0)
    mem.write(0x0, 0x12, only_byte=True)
    mem.write(0x1, 0x34, only_byte=True)
    mem.write(0x2, 0x56, only_byte=True)
    mem.write(0x3, 0x78, only_byte=True)
    assert(mem.data[0] == 0x78563412)

def test_cache_read_word():
    mem = Memory(lines=2**8, delay=1)
    mem.data = list(range(2**8))
    cache = Cache(lines=2**4, words_per_line=4, delay=0, next_level=mem)
    assert(cache.read(0x8) == 'wait')
    assert(cache.read(0x8)[0] == 2)

def test_cache_read_word():
    mem = Memory(lines=2**8, delay=0)
    mem.data = list(range(2**8))
    cache = Cache(lines=2**4, words_per_line=4, delay=0, next_level=mem)

    # Write words to the four words stored  in cache line 1
    cache.write(0x0, 0x0)
    cache.write(0x4, 0x1)
    cache.write(0x8, 0x2)
    cache.write(0xC, 0x3)

    # With four words per line, all four should appear in cache line 1
    # First value is tag = 0, last value is valid=1
    assert(cache.data[0] == [0, 0x0, 0x1, 0x2, 0x3, 1])

def test_cache_read_byte():
    mem = Memory(lines=2**8, delay=1)
    mem.data[0] = 1
    # mem has data: 0x0: 1, 0x1: 0, 0x2: 0, 0x3: 0
    cache = Cache(lines=2**4, words_per_line=4, delay=0, next_level=mem)
    assert(cache.read(0, only_byte=True) == 'wait')
    assert(cache.read(0, only_byte=True)[0] == 1)
    assert(cache.read(1, only_byte=True)[0] == 0)
    assert(cache.read(2, only_byte=True)[0] == 0)
    assert(cache.read(3, only_byte=True)[0] == 0)

def test_cache_write_byte():
    mem = Memory(lines=2**8, delay=0)
    cache = Cache(lines=2**4, words_per_line=1, delay=0, next_level=mem)

    cache.write(0x0, 0x0, only_byte=True)
    cache.write(0x1, 0x1, only_byte=True)
    cache.write(0x2, 0x2, only_byte=True)
    cache.write(0x3, 0x3, only_byte=True)
    assert(cache.data[0][1] == 0x03020100)

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
