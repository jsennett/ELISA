"""

Josh Sennett
Yash Adhikari
CS 535

"""
import pprint 
import sys


cycle = 1
def reset_cycle():
    global cycle
    cycle = 1


class Memory:

    def __init__(self, lines, words_per_read=4, delay=10, noisy=False, name="Memory"):
        self.lines = lines
        self.bits_per_line = lines.bit_length() - 1
        self.words_per_read = words_per_read
        self.bits_per_offset = words_per_read.bit_length() - 1
        self.data = [0] * lines
        self.initial_delay = delay
        self.current_delay = delay
        self.noisy = noisy
        self.name = name

    def get_data(self):
        return self.data

    def read(self, memory_address):
        global cycle

        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:
            start = memory_address >> self.bits_per_offset << self.bits_per_offset
            self.current_delay = self.initial_delay
            return self.data[start: start + self.words_per_read]

    def write(self, memory_address, value):
        global cycle
        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1

        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:
            self.current_delay = self.initial_delay
            self.data[memory_address] = value

    def print_data(self):
        # TODO - don't hard code field length
        for idx, line in enumerate(self.data):
            pprint.pprint('{:0{x}b} - {:032b}'.format(idx, line, x=self.bits_per_line))


class Cache:

    def __init__(self, lines, words_per_line=4, delay=3, address_length=8, next_level=None, top_level=False, noisy=False, name="Cache"):
        self.lines = lines
        self.words_per_line = words_per_line
        self.address_length = address_length
        self.bits_per_tag = (address_length-1).bit_length()
        self.bits_per_index = (lines - 1).bit_length()
        self.bits_per_offset = (words_per_line - 1).bit_length()
        self.next_level = next_level
        self.initial_delay = delay
        self.current_delay = delay
        self.top_level = top_level
        self.noisy = noisy
        self.name = name

        self.data = [[0] * 5 + [1]] * lines
        print("Cache created; {} lines, {} words per line".format(self.lines, self.words_per_line))
        print("{} bits per tag, {} bits per index, {} bits per offset".format(self.bits_per_tag, self.bits_per_index, self.bits_per_offset))

    def get_data(self):
        return self.data

    def read(self, memory_address):
        global cycle

        tag, index, offset = self.parse_address(memory_address)

        # Cache miss / invalid
        if self.data[index][5] != 0 or self.data[index][0] != tag:

            response = "wait"
            while response == "wait":
                response = self.next_level.read(memory_address)

            # Update
            self.data[index][0] = tag           # Update the tag
            self.data[index][1:5] = response    # Update the cache
            self.data[index][5] = 0             # Set the invalid bit to valid

        # The data is now in cache
        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:
            self.current_delay = self.initial_delay
            if self.top_level:
                return self.data[index][offset + 1]
            else:
                return self.data[index][1:5]

    def parse_address(self, memory_address):
        tag = memory_address >> (self.address_length - self.bits_per_tag)
        offset = memory_address & (2**self.bits_per_offset-1)
        index = (memory_address >> self.bits_per_offset) & (2**self.bits_per_index - 1)

        # Assert this is correct
        assert(memory_address == offset +
                                (index << self.bits_per_offset) + 
                                (tag << (self.bits_per_offset + self.bits_per_index)))
        return tag, index, offset


    def write(self, memory_address, value):
        global cycle
        tag, index, offset = self.parse_address(memory_address)

        # If the data is in cache
        if self.data[index][0] == tag:

            # Then, write to cache first
            if self.noisy:
                input("cycle: {}".format(cycle))
            cycle += 1
            self.current_delay -= 1
            if self.current_delay > 0:
                return "wait"
            else:
                self.data[index][offset + 1] = value        # Update the cache
                self.data[index][5] = 0                     # Set the invalid bit to valid
                self.current_delay = self.initial_delay     # Reset the current delay

        # In either case, write to memory
        response = "wait"
        while response == "wait":
            response = self.next_level.write(memory_address, value)

    def print_data(self):
        # TODO - don't hard code field length

        for idx, line in enumerate(self.data):
            formatted_line = '{:0{tag}b}'.format(idx, tag=self.bits_per_tag)
            for offset in range(self.words_per_line):
                formatted_line += ' - {:032b}'.format(line[offset+1])
            formatted_line += ' - {:01b}'.format(line[self.words_per_line + 1])            
            print(formatted_line)

class MemoryDemo:

    def __init__(self, memory_heirarchy):
        # TODO: don't hard code values, maybe accept as command line arguments
        assert(type(memory_heirarchy) == list and len(memory_heirarchy) > 0)
        self.memory_heirarchy = memory_heirarchy

    def execute_instructions(self, filename):

        # If an assembly file is specified, get instructions from file
        if filename is not None:
            instructions = self.parse_asm(filename)
            for instruction in instructions:
                self.execute(instruction)
                input("    [Press Enter to move to the next instruction]")

        # If no aseembly file is specified, get instructions from user
        else:
            self.help()
            while True:
                instruction = input(">>> ").split()
                if len(instruction) == 0:
                    continue
                self.execute(instruction)

    def execute(self, instruction):
        global cycle

        # Execute instructions until completed.
        start_time = cycle
        if instruction[0] == "load":
            response = self.load(int(instruction[1], 2))
            print(" ".join(instruction), "- value {:032b} loaded from address {} in {} cycles.".format(response, instruction[1], cycle - start_time))
        elif instruction[0] == "store":
            self.store(int(instruction[1], 2), int(instruction[2], 2))
            print(" ".join(instruction), "- value {} stored to address {} in {} cycles.".format(instruction[2], instruction[1], cycle - start_time))
        elif instruction[0] == "show":
            for level in self.memory_heirarchy:
                if level.name == instruction[1]:
                    level.print_data()
        elif instruction[0] == "quit":
            sys.exit(0)
        else:
            self.help()


    def load(self, memory_address):
        response = "wait"
        while response == "wait":
            response = self.memory_heirarchy[0].read(memory_address)
        return response

    def store(self, memory_address, value):
        response = "wait"
        while response == "wait":
            response = self.memory_heirarchy[0].write(memory_address, value)

    def parse_asm(self, filename):
        with open(filename) as f:
            instructions = [line.split() for line in f.read().split('\n') if line != '']
        return instructions

    def help(self):
        print("******** How to specify instructions: ********")
        print("    load  <ADDRESS>                |    load a value from memory")
        print("    store <ADDRESS> <VALUE>        |    store value in memory")
        print("    show  <CACHE_NAME>             |    show contents of memory or cache named <CACHE_NAME>")
        print("    help                           |    show help messages")
        print("    quit                           |    quit")


    def __str__(self):
        # TODO: nicely format a string
        pass
