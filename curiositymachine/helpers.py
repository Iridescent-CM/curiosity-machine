import string
import random

def random_string(length=5):
    char_list = list(map(lambda x: str(x).upper(), list(string.ascii_lowercase) + list(range(0,10))))
    return "".join(random.choice(char_list) for _ in range(length))
