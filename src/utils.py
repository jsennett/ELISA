import struct

def b_to_f(binary):
    return struct.unpack('f', struct.pack('I', binary))[0]

def f_to_b(decimal):
    return struct.unpack('I', struct.pack('f', decimal))[0]
