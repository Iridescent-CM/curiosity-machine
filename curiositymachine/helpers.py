import string
import random

# no vowels to avoid accidental word generation
# no l to avoid I/l confusion
CHARS = list('bcdfghjkmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ0123456789')

def random_string(length=5):
    return "".join(random.choice(CHARS) for _ in range(length))
