from itertools import count


def local_variable_name_generator():
    for i in count():
        yield f"__checkpointing_local_var_{i}__"
