import random
import string


def get_random_name() -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(20))
