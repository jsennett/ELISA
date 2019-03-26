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
import logging
# logging.basicConfig(level=logging.INFO)


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

    def read(self, memory_address, words_requested=1):
        """Get a block of values containing the input memory address
        
        Args:
            memory_address (int): Memory address
            words_requested (int): How many words to return (line size)
        
        Returns:
            list: A block of values including that memory address
                or
            str: a message to wait
        """
        # logging.info('read()')
        # If delay remains
        if self.current_delay > 0:
            self.current_delay -= 1
            return "wait"

        # If delay is finished
        else:
            self.current_delay = self.initial_delay # reset delay

            # Return the entire block
            bits_per_words_requested = words_requested.bit_length() - 1

            # TODO: memory_address actually refers to line number; divide start//4 to actually uses memory_address
            # This will require changing all points that use self.data[memory_address] -> self.data[memory_address//4]
            start = memory_address >> bits_per_words_requested << bits_per_words_requested
            return self.data[start: start + words_requested]

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
        # If delay remains
        if self.current_delay > 0:
            self.current_delay -= 1
            return "wait"

        # If delay is finished
        else:
            self.current_delay = self.initial_delay
            self.data[memory_address] = value

    def print_data(self):
        """Display memory contents in a console"""
        for idx, line in enumerate(self.data):
            print('({:0{x}b})  |  {:032b}'.format(idx, line, x=self.address_length))

    def __str__(self):
        return ("<Memory name: {}: ".format(self.name) + 
            "lines: {}".format(self.lines) + '; ' + 
            "address_length: {}".format(self.address_length) + '; ' + 
            "initial_delay: {}".format(self.initial_delay) + '; ' + 
            "current_delay: {}".format(self.current_delay) + '; ' + 
            "noisy: {}".format(self.noisy) + '; ' + 
            ">")


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

    # TODO: Enforce that all levels of cache have the same number of words per line
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
        
    def read(self, memory_address, words_requested=1):
        """Get a block of values containing the input memory address
        
        Args:
            memory_address (int): Memory address
            words_requested (int): How many words to return (line size)
        
        Returns:
            list: A block of values including that memory address
                or
            str: a message to wait

        # TODO: change words_requested to be either single word or full block; 
        # and not flexible number of words
        """
        # If delay remains
        if self.current_delay > 0:
            self.current_delay -= 1
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

                # Ask lower level and return their response
                response = self.next_level.read(memory_address, words_requested=self.words_per_line)
                if response == "wait":
                    return "wait"
                # If the lower level response with a value, save in cache before returning to caller
                else:
                    # Determine location where to save the value
                    if invalid_in_set:
                        row_location = first_invalid_row
                    else:
                        # Random replacement
                        row_location = random.randrange(start_index, end_index)
                
                # Update the values of the line
                self.data[row_location][0] = tag                         # Update the tag
                self.data[row_location][1: self.words_per_line + 1] = response     # Update the cache
                self.data[row_location][self.valid_bit_index] = 1        # Set the invalid bit to valid
                
            # Reset the delay
            self.current_delay = self.initial_delay
            
            # If top level cache, return the word in the cache line
            if words_requested == 1:
                return self.data[row_location][1 + offset: 2 + offset]
            else:
                return self.data[row_location][1: 1 + self.words_per_line]


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
            if self.current_delay > 0:
                self.current_delay -= 1
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
        return ("<Cache name: {}: ".format(self.name) + 
            "lines: {}".format(self.lines) + '; ' + 
            "words_per_line: {}".format(self.words_per_line) + '; ' + 
            "associativity: {}".format(self.associativity) + '; ' + 
            "address_length: {}".format(self.address_length) + '; ' + 
            "bits_per_index: {}".format(self.bits_per_index) + '; ' + 
            "bits_per_offset: {}".format(self.bits_per_offset) + '; ' + 
            "bits_per_tag: {}".format(self.bits_per_tag) + '; ' + 
            "next_level: {}".format(self.next_level.name) + '; ' + 
            "initial_delay: {}".format(self.initial_delay) + '; ' + 
            "current_delay: {}".format(self.current_delay) + '; ' + 
            "noisy: {}".format(self.noisy) + '; ' + 
            "valid_bit_index: {}".format(self.valid_bit_index) +
            ">")
