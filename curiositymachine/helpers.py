import string
import random

def random_string(length=5, lists_num=1):
    char_list = list(map(lambda x: str(x).upper(), list(string.ascii_lowercase) + list(range(0,10))))
    lists = []
    for _ in range(0, lists_num):
        lists.extend(char_list)
    return "".join(random.sample(lists, length))