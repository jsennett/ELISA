# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 13:09:48 2019

@author: ayash
"""
import random
f= open("instructions.txt","w+")
for i in range(1000):
     load_or_store = random.randrange(0,10)
     address = random.randrange(0, 256)
     if load_or_store == 0:
         value = random.randrange(0, 2^32)
         f.write("store {} {}\n".format(bin(address), bin(value)))
     else:
         f.write("load {}\n".format(bin(address)))
f.close()   