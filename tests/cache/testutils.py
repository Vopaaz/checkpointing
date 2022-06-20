import pathlib
import shutil

tmpdir = pathlib.Path(".checkpointing-unit-test-tmp")


def teardown_module():
    rmdir_func()


def rmdir_func():
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
