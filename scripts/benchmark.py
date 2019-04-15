import sys
sys.path.append("src/")
from simulator import Simulator

def run_benchmark(caching=True, pipelining=True):
    simulator = Simulator()

    DRAM = Memory(lines=2**12, delay=0)
    if caching:
        L3 = Cache(lines=2**8, delay=0, next_level=DRAM)
        L2 = Cache(lines=2**8, delay=0, next_level=L3)
        L1 = Cache(lines=2**8, delay=0, next_level=L2)
        memory_heirarchy = [L1, L2, L3, DRAM]
    else:
        memory_heirarchy = [DRAM]
    instructions, data = assemble_to_numerical(instruction)

def main():
    # Run benchmarks for different cache configurations
    for
    pass

if __name__ == "__main__":
    main()
