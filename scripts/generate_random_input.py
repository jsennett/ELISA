import random
import time

def generate_exchange_sort():
    for length in [2**i for i in range(3, 20)]:

        # Generate randomly ordered ints 0 to length
        random_ints = random.choices(list(range(0, length)), k=length)

        # Modify the exchange sort assembly file to include this data
        infile = 'scripts/exchange_sort/exchange_sort_format.asm'
        with open(infile, 'r') as f:
            text_instructions = f.read()

        text_instructions += "    array: {}\n".format(str(random_ints))
        text_instructions += "    length: {}\n".format(length)

        outfile = 'scripts/exchange_sort/exchange_sort_{length}w.asm'.format(length=length)
        with open(outfile, 'w') as f:
            f.write(text_instructions)
            print("saved file {}".format(outfile))


if __name__ == '__main__':
    generate_exchange_sort()
