import pathlib
import shutil

tmpdir = pathlib.Path(".checkpointing-unit-test-tmp")


def rmdir_func():
    if tmpdir.exists():
        shutil.rmtree(tmpdir)


def mkdir_func():
    if not tmpdir.exists():
        tmpdir.mkdir()
