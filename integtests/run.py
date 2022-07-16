import subprocess
from itertools import count
import pathlib
import shutil
import textwrap
from checkpointing import defaults
from termcolor import cprint

cwd = pathlib.Path().cwd()
workspace = pathlib.Path("testworkspace")
checkpoints = pathlib.Path(defaults["cache.filesystem.directory"])


class TestDefinitionError(RuntimeError):
    pass


class TestFailedError(RuntimeError):
    pass


def copy_file_to_workplace(f: pathlib.Path):
    if f.is_file():
        shutil.copy(f, workspace.joinpath(f.name))
    else:
        raise TestDefinitionError(f"{f} should be a file.")


def remove_file_in_workplace(f: pathlib.Path):
    """f is the path of file in the case folder, not the workspace folder."""
    if f.is_file():
        workspace.joinpath(f.name).unlink()
    else:
        raise TestDefinitionError(f"{f} should be a file.")


def sanitize(s: str):
    s = s.replace("\r\n", "\n").replace("\r", "\n").strip()
    s = "\n".join([s0.strip() for s0 in s.split("\n")])
    return s


def run_case(case_name):

    casepath = pathlib.Path(".").joinpath("integtests", case_name)
    resourcepath = casepath.joinpath("resources")

    if workspace.exists():
        shutil.rmtree(workspace)

    if checkpoints.exists():
        shutil.rmtree(checkpoints)

    workspace.mkdir()

    if resourcepath.exists():  # Resource setup
        for f in resourcepath.iterdir():
            copy_file_to_workplace(f)

    for i in count():
        wspath = casepath.joinpath(f"workspace{i}")
        outputpath = casepath.joinpath("outputs", f"output{i}.txt")

        if not wspath.exists():
            break

        for f in wspath.iterdir():  # Script setup
            copy_file_to_workplace(f)

        if not outputpath.exists():
            raise TestDefinitionError(f"Case {i} for {case_name} has script definition, but no expected output")

        with open(outputpath, mode="r", encoding="utf-8") as f:
            expected = sanitize(f.read())

        p = subprocess.run(
            ["py", "-3", "-m", f"{workspace.name}.main"],
            capture_output=True,
            cwd=cwd,
        )

        actual = sanitize(p.stdout.decode("utf-8"))

        if expected != actual:
            raise TestFailedError(
                f"""
Test failed in {case_name}, workspace{i}.

<Expected>
{expected}

<Actual>
{actual}
                """.strip()
            )

        for f in wspath.iterdir():  # Script teardown
            remove_file_in_workplace(f)

    shutil.rmtree(workspace)

    if i == 0:
        raise TestDefinitionError(f"No workspace exists for case {case}, at least 1 is expected.")


def find_cases():
    for d in pathlib.Path(".").joinpath("integtests").iterdir():
        if d.is_dir() and d.name != "__pycache__":
            yield d


if __name__ == "__main__":

    cprint("Integration tests:")

    failed = []
    passed = 0

    for case in find_cases():

        case_name = case.name
        cprint(f"Running case: {case_name}", end=" ")

        try:
            run_case(case_name)

        except TestDefinitionError as e:
            cprint(f"Definition Error: {e}", "red")
            failed.append(case_name)

        except TestFailedError as e:
            cprint(f"Failed: {e}", "red")
            failed.append(case_name)

        else:
            cprint("Passed", "green")
            passed += 1

    cprint(f"Total passed: {passed}", "green")
    if failed:
        cprint(f"Total failed: {len(failed)}", "red")
        cprint("Failed tests:", "red")
        cprint(", ".join(failed), "red")
