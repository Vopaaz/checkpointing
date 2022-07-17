# Integration Tests

`checkpointing` caches results between different executions of a Python program with potential code changes. 
As a result, common unit tests cannot be applied to test its end-to-end functionality.

This folder contains "integration tests", which simulates the code changes and executions,
and see of the program output (in the stdout) is as expected.

## Test Structure

A test case is a folder in this directory with the following subdirectories:
- `workspaces`
- `outputs`

The `workspaces` folder contains subdirectories named `workspace0`, `workspace1`, etc.
Each `workspaceN` represents the code in a project in a certain time point.
It can contain any arbitrary file, but in general a `main.py` is expected, as it will be used as the entry point.

The `outputs` folder contains files named `output0.txt`, `output1.txt`, etc.
Each `outputN.txt` represents the expected output (in the stdout) for running the `main.py` in `workspaceN`.

In each test case, the contents of the `workspaceN` folders will be copied to a global workspace (`$projectRoot/testworkspace`) and executed one after the other.
In this way we ensure that the code files with the same name actually have the same path,
and thus simulating code changes.
The stdout will be captured and compared to `outputN.txt`. If there is a mismatch, the test case will fail.
The following command is used for the execution:
```bash
$ python -m testworkspace.main
```
After each execution, the `testworkspace` will be cleaned up to prepare for loading the next `workspace`.

The folder structure can be nested to represent the hierarchy of the test,
however, please be aware to avoid `workspaces` and `outputs` as the name of a non-test-case folder.

An optional `Readme.md` can be created anywhere in the directories to illustrate the purpose of a test or a group of tests.

The script `run.py` is the entry of running the integration tests.

## Executing the Integration Test

First make sure that your `python` command is pointing to the interpreter of your desired version and environment, using `which python`.

Then, in project root, run
```bash
$ python -m integtests.run
```


Note that the `python` command is hardcoded in `run.py` so even if you `python3` or `py -3` to launch the test script, 
the actual testings would not work.



