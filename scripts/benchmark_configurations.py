from memory import Cache, Memory

MEMORY_ACCESS_TIME = 10

DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
dram_only = {
    'memory_heirarchy': [DRAM],
    'pipeline_enabled': True,
    'name': 'dram_only'
}

DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
L1 = Cache(lines=2**10, delay=0, next_level=DRAM)
L1_caching = {
    'memory_heirarchy': [L1, DRAM],
    'pipeline_enabled': True,
    'name': 'L1_caching'
}


DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
L2 = Cache(lines=2**12, delay=3, next_level=DRAM)
L1 = Cache(lines=2**10, delay=0, next_level=L2)
L2_caching = {
    'memory_heirarchy': [L1, L2, DRAM],
    'pipeline_enabled': True,
    'name': 'L2_caching'
}

DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
L3 = Cache(lines=2**14, delay=3, next_level=DRAM)
L2 = Cache(lines=2**12, delay=3, next_level=L3)
L1 = Cache(lines=2**10, delay=0, next_level=L2)
L3_caching = {
    'memory_heirarchy': [L1, L2, L3, DRAM],
    'pipeline_enabled': True,
    'name': 'L3_caching'
}

DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
dram_only_no_pipelining = {
    'memory_heirarchy': [DRAM],
    'pipeline_enabled': False,
    'name': 'dram_only_no_pipelining'
}

DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
L1 = Cache(lines=2**10, delay=0, next_level=DRAM)
L1_caching_no_pipelining = {
    'memory_heirarchy': [L1, DRAM],
    'pipeline_enabled': False,
    'name': 'L1_caching_no_pipelining'
}


DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
L2 = Cache(lines=2**12, delay=3, next_level=DRAM)
L1 = Cache(lines=2**10, delay=0, next_level=L2)
L2_caching_no_pipelining = {
    'memory_heirarchy': [L1, L2, DRAM],
    'pipeline_enabled': False,
    'name': 'L2_caching_no_pipelining'
}

DRAM = Memory(lines=2**20, delay=MEMORY_ACCESS_TIME)
L3 = Cache(lines=2**14, delay=3, next_level=DRAM)
L2 = Cache(lines=2**12, delay=3, next_level=L3)
L1 = Cache(lines=2**10, delay=0, next_level=L2)
L3_caching_no_pipelining = {
    'memory_heirarchy': [L1, L2, L3, DRAM],
    'pipeline_enabled': False,
    'name': 'L3_caching_no_pipelining'
}

configurations = [dram_only, L1_caching, L2_caching, L3_caching,
                  dram_only_no_pipelining, L1_caching_no_pipelining,
                  L2_caching_no_pipelining, L3_caching_no_pipelining]

