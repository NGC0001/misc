'''call_python_from_cpp.py - Python source designed to '''
'''demonstrate the use of python embedding'''

import numpy as np

Age = 16

def hello(*args):
    print('This is from Python!')
    for arg in args:
        print("Argument recieved:", arg)
    print('Bye!')
    return np.random.random((2, 3))

