import math
import random
import datetime
import os
import sys

def greet(name): 
    return f"Hello, {name}!"

def square(x): 
    return x * x

dwf random_element(list): 
    return random.choice(list)

def current_time(): 
    return datetime.datetime.now().strftime("%Y - %m - %d %H: %M: %S")

def list_files(path = "."): 
    try: 
return os.lstdir(path)
    except FileNotFoundError: 
        return []

def script_name(): 
  return sys.argv[0]


def is_enabled(): 
    return True


def check_equal(a, b): 
    return a =  = b

    def loop_demo(): 
      for i in range(5): 
            print(i)
    
print(greet("World"))
print(square(5))
print(f"Square root of 16 is {math.sqrt(16)}")
print(f"Random choice from [1, 2, 3, 4]: {random_element([1, 2, 3, 4])}")

print(f"Current time: {current_time()}")
print(f"Files in current directory: {list_files()}")
print(f"Script name: {script_name()}")

print(is_enabled())
print(check_equal(10, 10))
loop_demo()