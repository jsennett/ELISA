import struct

def b_to_f(binary):
    """Convert binary to floating point"""
    return struct.unpack('f', struct.pack('I', binary))[0]

def f_to_b(decimal):
    """Convert binary to floating point"""
    return struct.unpack('I', struct.pack('f', decimal))[0]
