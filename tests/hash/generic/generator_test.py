from checkpointing.hash import hash_anything
from itertools import count

def gen_1():
    for i in count():
        yield i

def gen_2():
    for i in count():
        yield i

def test_hash_generator():
    g1 = gen_1()
    g2 = gen_2()
    assert hash_anything(g1) != hash_anything(g2)


def test_hash_generator_definition():
    assert hash_anything(gen_1) != hash_anything(gen_2)