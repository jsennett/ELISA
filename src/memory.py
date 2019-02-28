"""

Josh Sennett
Yash Adhikari
CS 535

"""

import random

cycle = 1
def reset_cycle():
    global cycle
    cycle = 1

class Memory:

    def __init__(self, lines, words_per_read=4, delay=10, noisy=False):
        self.lines = lines
        self.bits_per_line = lines.bit_length() - 1
        self.words_per_read = words_per_read
        self.bits_per_offset = words_per_read.bit_length() - 1
        self.data = [0] * lines
        self.initial_delay = delay
        self.current_delay = delay
        self.noisy = noisy

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

    def __str__(self):
        # TODO: nicely format a string
        pass


class Cache:
    
    def __init__(self, lines, associativity=2, words_per_line=4, delay=3, address_length=8, next_level=None, top_level=False, noisy=False):
        self.lines = lines
        self.words_per_line = words_per_line
        self.associativity = associativity
        self.address_length = address_length
        self.bits_per_index = (lines//associativity - 1).bit_length()
        self.bits_per_offset = (words_per_line - 1).bit_length()
        self.bits_per_tag = address_length - self.bits_per_index - self.bits_per_offset
        self.next_level = next_level
        self.initial_delay = delay
        self.current_delay = delay
        self.top_level = top_level
        self.noisy = noisy

        self.data = [[0] * (words_per_line+1) + [0]] * lines
        print("Cache created; {} lines, {} words per line; {} associativity".format(self.lines, self.words_per_line, self.associativity))
        print("{} bits per tag, {} bits per index, {} bits per offset".format(self.bits_per_tag, self.bits_per_index, self.bits_per_offset))

    def get_data(self):
        return self.data

    def read(self, memory_address):
        global cycle
        print("read() at delay", self.current_delay)

        # The data is now in cache
        if self.noisy:
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:

            tag, index, offset = self.parse_address(memory_address)
            start_index = index*self.associativity
            end_index = start_index + self.associativity
            
            # Cache miss / invalid
            tag_in_set = False
            invalid_in_set = False
            row_location = None
            for row_index in range(start_index, end_index):
                print("checking row with contents:", self.data[row_index], "at index", row_index)
                
                # If we haven't found an invalid row yet, and if the current row is invalid
                if not invalid_in_set and self.data[row_index][5] == 0:
                    first_invalid_row = row_index
                    invalid_in_set = True
                
                # Tag is in the set, but may be valid or invalid
                if self.data[row_index][0] == tag:
                    tag_in_set = True
                    row_location = row_index
                    row_is_valid = (self.data[row_index][5] == 1)                    
                    
            print("row location", row_location)
            print("tag in set?", tag_in_set, "invalid in set?", invalid_in_set)
                
            # Cache miss - the tag is not in the set, or the tag is in set but invalid            
            if not tag_in_set or not row_is_valid:          
                print("cache miss.")
    
                response = "wait"
                while response == "wait":
                    response = self.next_level.read(memory_address)
                
                # If the 
                if invalid_in_set:
                    print("there is an empty row in the set")
                    row_location = first_invalid_row
                    # print(row_location)
                else:
                    row_location = random.randrange(start_index, end_index)
                    print("all rows in set are full. Putting at row", row_location)
                    
                print("before", self.data)
                print("Updating row", row_location, "to have tag", tag)
                print('\n', self.data[row_location][0])
                print(self.data[row_location][1:5])
                print(self.data[row_location][5], '\n')
                self.data[row_location][0] = tag           # Update the tag
                self.data[row_location][1:5] = response    # Update the cache
                self.data[row_location][5] = 1             # Set the invalid bit to valid
                print("after", self.data)

            self.current_delay = self.initial_delay
            
            if self.top_level:
                
                # for debugging:
                for row_index in range(start_index, end_index):
                    print(self.data[row_index], row_index)
                
                return self.data[row_location][offset + 1]
            else:
                return self.data[row_location][1:5]

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
                self.data[index][5] = 1                     # Set the invalid bit to valid
                self.current_delay = self.initial_delay     # Reset the current delay

        # In either case, write to memory
        response = "wait"
        while response == "wait":
            response = self.next_level.write(memory_address, value)


class MemoryDemo:

    def __init__(self, memory_heirarchy):
        # TODO: don't hard code values, maybe accept as command line arguments
        assert(type(memory_heirarchy) == list and len(memory_heirarchy) > 0)
        self.memory_heirarchy = memory_heirarchy

    def execute(self, instructions):
        global cycle

        for instruction in instructions:

            start_time = cycle
            arguments = instruction.split()

            if arguments[0] == "load":
                response = self.load(int(arguments[1], 2))
                print(instruction, "- value {:032b} loaded from address {} in {} cycles.".format(response, arguments[1], cycle - start_time))
            elif arguments[0] == "store":
                self.store(int(arguments[1], 2), int(arguments[2], 2))
                print(instruction, "- value {} stored to address {} in {} cycles.".format(arguments[2], arguments[1], cycle - start_time))

            start_time = cycle

    def load(self, memory_address):
        response = "wait"
        while response == "wait":
            response = self.memory_heirarchy[0].read(memory_address)
        return response


    def store(self, memory_address, value):
        response = "wait"
        while response == "wait":
            response = self.memory_heirarchy[0].write(memory_address, value)

    def __str__(self):
        # TODO: nicely format a string
        pass
