cycle = 1


class Memory:

    def __init__(self, lines, words_per_read=4, delay=10, mode="noisy"):
        self.lines = lines
        self.bits_per_line = lines.bit_length() - 1
        self.words_per_read = words_per_read
        self.bits_per_offset = words_per_read.bit_length() - 1
        self.data = [0] * lines
        self.initial_delay = delay
        self.current_delay = delay
        self.mode = mode
        print("Memory created; {} lines, {} bits.".format(self.lines, self.lines.bit_length() - 1))

    def get_data(self):
        return self.data

    def read(self, memory_address):
        global cycle

        if self.mode == "noisy":
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:
            start = memory_address >> 2 << 2
            self.current_delay = self.initial_delay
            return self.data[start: start + 4]

    def write(self, memory_address, value):
        global cycle
        if self.mode == "noisy":
            input("cycle: {}".format(cycle))
        cycle += 1

        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:
            self.current_delay = self.initial_delay
            self.data[memory_address] = value


class Cache:

    def __init__(self, lines, words_per_line=4, delay=3, address_length=8, next_level=None, mode="noisy"):
        self.lines = lines
        self.words_per_line = words_per_line
        self.address_length = address_length
        self.bits_per_tag = (address_length-1).bit_length()
        self.bits_per_index = (lines - 1).bit_length()
        self.bits_per_offset = (words_per_line - 1).bit_length()
        self.next_level = next_level
        self.initial_delay = delay
        self.current_delay = delay
        self.mode = mode

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
            self.data[index][5] = 0             # Set the invalid bit to clean

        # The data is now in cache
        if self.mode == "noisy":
            input("cycle: {}".format(cycle))
        cycle += 1
        self.current_delay -= 1
        if self.current_delay > 0:
            return "wait"
        else:
            self.current_delay = self.initial_delay
            return self.data[index][offset + 1]

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
            if self.mode == "noisy":
                input("cycle: {}".format(cycle))
            cycle += 1
            self.current_delay -= 1
            if self.current_delay > 0:
                return "wait"
            else:
                self.data[index][offset + 1] = value        # Update the cache
                self.data[index][5] = 0                     # Set the invalid bit to clean
                self.current_delay = self.initial_delay     # Reset the current delay

        # In either case, write to memory
        response = "wait"
        while response == "wait":
            response = self.next_level.write(memory_address, value)


class MemoryDemo:

    def __init__(self, mode="noisy"):
        # TODO: don't hard code values, maybe accept as command line arguments
        self.DRAM = Memory(lines=2**8, delay=10, mode=mode)
        self.L1 = Cache(lines=8, words_per_line=4, delay=3, next_level=self.DRAM, mode=mode)
        self.current_cycle = 0

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
            response = self.L1.read(memory_address)
        return response


    def store(self, memory_address, value):
        response = "wait"
        while response == "wait":
            response = self.L1.write(memory_address, value)


if __name__ == '__main__':

    # Memory Demo
    instructions = [
        "load 0b00000000",                  # 13
        "load 0b00000000",                  # 3
        "load 0b00000000",                  # 3
        "store 0b01101011 0b00000001",      # 10
        "load 0b01101011",                  # 13
        "store 0b01101011 0b00000001"       # 13
    ]

    demo = MemoryDemo(mode="not noisy")
    demo.execute(instructions)