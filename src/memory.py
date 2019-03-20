"""

Josh Sennett
Yash Adhikari
CS 535

Note: several characteristics of the memory classes 
are not designed to be customized, such as:
    - word size is 32 bits
    - memory is word addressable
    - Caching is write-through (write hit -> immediate write to cache and memory)
        and no allocate (write miss -> write immediately to memory, skipping cache)


# TODO:
- Ensure that tag length is correctly calculated based on the next level's address space,
associativity, cache size, and words per line. - Done, I think.
    - Add docstrings
    - Customize / prepare for demos
"""
import sys
import random

cycle = 1
cache_miss = 0
total_loads = 0


def reset_metrics():
    """Reset metrics used for tracking cache performance.
    """
    global cycle, cache_miss, total_loads
    cycle, cache_miss, total_loads = 1, 0, 0


class Memory:
    """Memory is a array-based memory structure that supports read and write operations.  
    
    Attributes:
        address_length (int): bits per address
        current_delay (int): cycles per read or write
        data (list of int): current data contents
        initial_delay (int): cycles remaining until read or write completes
        lines (int): lines of data
        name (str): handle (e.g. DRAM)
        noisy (bool): whether to pause after each cycle
    """
    
    def __init__(self, lines, delay=10, noisy=False, name="Memory"):
        """Initialize a Memory object."""
        self.lines = lines
        self.address_length = lines.bit_length() - 1
        self.data = [0] * lines
        self.initial_delay = delay
        self.current_delay = delay
        self.noisy = noisy
        self.name = name

    def reset_data(self):
        self.data = [0] * self.lines

    def read(self, memory_address, num_words=1):
        """Get a block of values containing the input memory address
        
        Args:
            memory_address (int): Memory address
            num_words (int): How many words to return (line size)
        
        Returns:
            list: A block of values including that memory address
                or
            str: a message to wait
        """
        global cycle, cache_miss

        # Cycle delay
        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1

        # If delay remains
        if self.current_delay > 0:
            return "wait"

        # If delay is finished
        else:
            self.current_delay = self.initial_delay # reset delay
            cache_miss += 1

            # Return the entire block
            bits_per_num_words = num_words.bit_length() - 1
            start = memory_address >> bits_per_num_words << bits_per_num_words
            return self.data[start: start + num_words]

    def write(self, memory_address, value):
        """Write a value to a memory_address

        Args:
            memory_address (int): Memory address
            value (int): Value to write
        
        Returns:
            str: a message to wait
                or
            NoneType: None, if the write is successful.
        """
        global cycle

        # Cycle delay
        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1

        # If delay remains
        if self.current_delay > 0:
            return "wait"

        # If delay is finished
        else:
            self.current_delay = self.initial_delay
            self.data[memory_address] = value

    def print_data(self):
        """Display memory contents in a console"""
        for idx, line in enumerate(self.data):
            print('({:0{x}b})  |  {:032b}'.format(idx, line, x=self.address_length))


class Cache:
    """Cache is a array-based memory structure that supports read and write operations.

    Attributes:
        address_length (int): bits per address
        associativity (int): rows per set (e.g. 1 for direct-mapped, 
                                           2 for 2-way set associative)
        bits_per_index (int): bits per index
        bits_per_offset (int): bits per offset
        current_delay (int): cycles per read or write
        data (list of list of int): current data contents. 
                                    Each row contains a cache line, containing
                                    tag, [words], and valid bit
        initial_delay (int): cycles remaining until read or write completes
        lines (int): lines of data
        name (str): handle (e.g. DRAM)
        noisy (bool): whether to pause after each cycle
        valid_bit_index (int): location of valid bit in line
        words_per_line (int): words per line
    """
    def __init__(self, lines, words_per_line=4, delay=3, associativity=1, next_level=None, noisy=False, name="Cache"):
        """Initialize a Cache object."""
        self.lines = lines
        self.words_per_line = words_per_line
        self.associativity = associativity
        self.address_length = next_level.address_length
        self.bits_per_index = (lines//associativity - 1).bit_length()
        self.bits_per_offset = (words_per_line - 1).bit_length()
        self.bits_per_tag = self.address_length - self.bits_per_index - self.bits_per_offset
        self.next_level = next_level
        self.initial_delay = delay
        self.current_delay = delay
        self.noisy = noisy
        self.name = name
        self.data = [[0] * (words_per_line+2) for line in range(lines)]
        self.valid_bit_index = (words_per_line + 1)

    def reset_data(self):
        self.data = [[0] * (self.words_per_line+2) for line in range(self.lines)]
        
    def read(self, memory_address, num_words=1):
        """Get a block of values containing the input memory address
        
        Args:
            memory_address (int): Memory address
            num_words (int): How many words to return (line size)
        
        Returns:
            list: A block of values including that memory address
                or
            str: a message to wait
        """
        global cycle

        # Cycle delay
        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1
        
        # If delay remains
        if self.current_delay > 0:
            return "wait"

        # If delay finished
        else:

            tag, index, offset = self.parse_address(memory_address)
            start_index = index*self.associativity
            end_index = start_index + self.associativity
            
            # Cache miss / invalid
            tag_in_set = False
            invalid_in_set = False
            row_location = None
            for row_index in range(start_index, end_index):
                
                # If we haven't found an invalid row yet, and if the current row is invalid
                if not invalid_in_set and self.data[row_index][self.valid_bit_index] == 0:
                    first_invalid_row = row_index
                    invalid_in_set = True
                
                # Tag is in the set, but may be valid or invalid
                if self.data[row_index][0] == tag:
                    tag_in_set = True
                    row_location = row_index
                    row_is_valid = (self.data[row_index][self.valid_bit_index] == 1)                    
                
            # Cache miss - the tag is not in the set, or the tag is in set but invalid            
            if not tag_in_set or not row_is_valid:
                response = "wait"
                while response == "wait":
                    response = self.next_level.read(memory_address, num_words=self.words_per_line)
                
                # If there is place to replace within the set
                if invalid_in_set:
                    row_location = first_invalid_row
                else:
                    row_location = random.randrange(start_index, end_index)
                
                # Update the values of the line
                self.data[row_location][0] = tag                         # Update the tag
                self.data[row_location][1: num_words + 1] = response     # Update the cache
                self.data[row_location][self.valid_bit_index] = 1        # Set the invalid bit to valid
                
            # Reset the delay
            self.current_delay = self.initial_delay
            
            # If top level cache, return the word in the cache line
            return self.data[row_location][1:num_words + 1]


    def parse_address(self, memory_address):
        """Parse tag, index, and offset from a memory address"""
        tag = memory_address >> (self.address_length - self.bits_per_tag)
        offset = memory_address & (2**self.bits_per_offset-1)
        index = (memory_address >> self.bits_per_offset) & (2**self.bits_per_index - 1)
        return tag, index, offset


    def write(self, memory_address, value):
        """Write a value to a lower level of memory.

        Args:
            memory_address (int): Memory address
            value (int): Value to write
        
        Returns:
            str: a message to wait
                or
            NoneType: None, if the write is successful.
        """
        global cycle

        # Calculate fields needed to handle the write
        tag, index, offset = self.parse_address(memory_address)
        start_index = index*self.associativity
        end_index = start_index + self.associativity
            
        # Find whether or not the data is in cache and row location
        tag_in_set = False
        row_location = None
        for row_index in range(start_index, end_index):

            # Tag is in the set, but may be valid or invalid
            if self.data[row_index][0] == tag:
                tag_in_set = True
                row_location = row_index
            
        # If cache hit, update cache first
        if tag_in_set:
            if self.noisy:
                input("cycle: {}".format(cycle))
            cycle += 1
            self.current_delay -= 1
            if self.current_delay > 0:
                return "wait"
            else:
                self.data[row_location][offset + 1] = value                     # Update the cache
                self.data[row_location][self.valid_bit_index] = 1               # Set the invalid bit to valid
                self.current_delay = self.initial_delay                         # Reset the current delay

        # In either case, write to memory
        response = "wait"
        while response == "wait":
            response = self.next_level.write(memory_address, value)

    def print_data(self):
        """Display cache contents in a console"""
        for idx, line in enumerate(self.data):
            formatted_line = '({:0{idx_len}b})  |  '.format(idx, idx_len=self.bits_per_index)
            formatted_line += '{:0{tag_len}b} '.format(line[0], tag_len=self.bits_per_tag)
            for offset in range(self.words_per_line):
                formatted_line += ' - {:032b}'.format(line[offset+1])
            formatted_line += ' - {:01b}'.format(line[self.words_per_line + 1])            
            print(formatted_line)

    def __str__(self):
        return ("<Cache name {}: ".format(self.name) + 
            "lines: {}".format(self.lines) + '\n\t' + 
            "words_per_line: {}".format(self.words_per_line) + '\n\t' + 
            "associativity: {}".format(self.associativity) + '\n\t' + 
            "address_length: {}".format(self.address_length) + '\n\t' + 
            "bits_per_index: {}".format(self.bits_per_index) + '\n\t' + 
            "bits_per_offset: {}".format(self.bits_per_offset) + '\n\t' + 
            "bits_per_tag: {}".format(self.bits_per_tag) + '\n\t' + 
            "next_level: {}".format(self.next_level.name) + '\n\t' + 
            "initial_delay: {}".format(self.initial_delay) + '\n\t' + 
            "current_delay: {}".format(self.current_delay) + '\n\t' + 
            "noisy: {}".format(self.noisy) + '\n\t' + 
            "valid_bit_index: {}".format(self.valid_bit_index) +
            ">")


class MemoryDemo:
    """Instance of a memory demo.
    
    Attributes:
        memory_heirarchy (TYPE): An ordered 
    """
    
    def __init__(self, memory_heirarchy):
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

            # Display initial instructions
            self.help()

            # Loop, requesting for user input
            while True:
                instruction = input(">>> ").split()
                self.execute(instruction)

    def execute(self, instruction):
        global cycle, cache_miss, total_loads
        
        # Ignore empty instructions
        if len(instruction) == 0:
            return

        # Execute instruction
        start_time = cycle
        if instruction[0] == "load":
            response = self.load(int(instruction[1], 2))
            print(" ".join(instruction), "- value {:032b} loaded from address {} in {} cycles.".format(response[0], instruction[1], cycle - start_time))
        elif instruction[0] == "store":
            self.store(int(instruction[1], 2), int(instruction[2], 2))
            print(" ".join(instruction), "- value {} stored to address {} in {} cycles.".format(instruction[2], instruction[1], cycle - start_time))
        elif instruction[0] == "show":
            for level in self.memory_heirarchy:
                if level.name == instruction[1]:
                    level.print_data()
        elif instruction[0] == "quit":
            sys.exit(0)
        elif instruction[0] == "describe":
            for level in self.memory_heirarchy:
                if level.name == instruction[1]:
                    print(level)

        # If the command is not recognized, send help
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
        print("")
        print("Memory and caches are named:")
        for level in self.memory_heirarchy:
            print('    ', level.name)
        print("")
