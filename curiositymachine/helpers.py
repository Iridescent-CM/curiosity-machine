import string
import random

CHARS = 'bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWZ0123456789'

def random_string(length=5):
    return "".join(random.choice(list(CHARS)) for _ in range(length))
