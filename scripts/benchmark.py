import time
import sys
sys.path.append("src/")
from simulator import Simulator
import assembler

sys.path.append("scripts/")
from benchmark_configurations import configurations

# Disable logging
import logging
logger = logging.getLogger()
logger.disabled = True

def benchmark_exchange_sort():

    outfile = open("scripts/results/exchange_sort.txt", 'w')
    outfile.write("name,pipeline_enabled,input_size,cycles,correct\n")


    # TODO: Expand to whole range of lengths
    for length in [2**3, 2**4, 2**5, 2**6, 2**7, 2**8, 2**9, 2**10, 2**11, 2**12]:

        # TODO: Increase number of configurations
        for configuration in configurations:

            simulator = Simulator()
            simulator.memory_heirarchy = configuration['memory_heirarchy']
            simulator.pipeline_enabled = configuration['pipeline_enabled']

            # Ensure memory is reset
            for level in simulator.memory_heirarchy:
                level.reset_data()

            # Assemble and set instructions
            infile = 'scripts/exchange_sort/exchange_sort_{length}w.asm'.format(length=length)
            with open(infile, 'r') as f:
                text_instructions = f.read()

            instructions, data = assembler.assemble_to_numerical(text_instructions)
            simulator.set_instructions(instructions, data)

            #power = 0
            start = time.time()
            while not simulator.end_of_program:
                simulator.step()
            duration = time.time() - start

                #if (simulator.cycle % 10**power) == 0:
                    #print(simulator.cycle)
                    #power += 1

            # TODO: if instruction length changes this will change too
            array_after_sort = simulator.memory_heirarchy[-1].data[27:27 + length]
            correctly_sorted = all(array_after_sort[i] <= array_after_sort[i+1]
                                   for i in range(length - 1))

            print("{} complete; took {} cycles ({:.2f} seconds). Correctly sorted? {}".format(configuration['name'], simulator.cycle, duration, correctly_sorted))
            configuration['name'], configuration['pipeline_enabled'], length, simulator.cycle, correctly_sorted

            outfile.write("{},{},{},{},{}\n".format(
                                        configuration['name'],
                                        configuration['pipeline_enabled'],
                                        length,
                                        simulator.cycle,
                                        correctly_sorted))
    outfile.close()

if __name__ == '__main__':
    benchmark_exchange_sort()
