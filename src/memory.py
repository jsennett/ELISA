
class Memory:

    def __init__(self, size, delay):
        self.size = size
        self.delay = delay
        self.data = [0x0000] * size
        self.associativity = "direct mapped"

    def read(self, address, cycles_remaining=None):

        if self.associativity == "direct mapped":
            # compare tag with 


        if cycles_remaining is None:
            cycles_remaining = self.delay

        if cycles_remaining > 0:
            input("Wait to read...")
            self.read(address, cycles_remaining-1)
        else:
            input(self.data[address])
            return self.data[address]

    def write(self, address, value, cycles_remaining=None):
        if cycles_remaining is None:
            cycles_remaining = self.delay

        if cycles_remaining > 0:
            input("Wait to write...")
            self.write(address, value, cycles_remaining-1)
        else:
            self.data[address] = value
            input("Write successful.")


if __name__ == '__main__':

    RAM = Memory(size=32, delay=10)

    print("read 0x0000")
    RAM.read(0x0000)

    print("write 0x0000 0x0001")
    RAM.write(0x0000, 0x0001)

    print("read 0x0000")
    RAM.read(0x0000)

    # TODO: Parse assembly instructions, convert into invocations
    # instructions = [
    #     ("read", 0x0000),
    #     ("write", 0x0000, 0x0001),
    #     ("read", 0x0000)        
    # ]














