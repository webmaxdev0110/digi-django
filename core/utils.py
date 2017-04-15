import random
import string

def rand_string(length=12):
   return ''.join(random.choice(string.lowercase) for i in range(length))