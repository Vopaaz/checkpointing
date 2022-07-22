import subprocess
from itertools import count
import pathlib
import shutil
import argparse
from checkpointing import defaults
from termcolor import cprint
import time

cwd = pathlib.Path().cwd()
workspace = pathlib.Path("testworkspace")
checkpointing_cache = pathlib.Path(defaults["cache.filesystem.directory"])
cachier_cache = pathlib.Path().home().joinpath(".cachier")
joblib_cache = pathlib.Path(".joblib")


class TestDefinitionError(RuntimeError):
    pass


class TestFailedError(RuntimeError):
    pass


def copy_file_to_workplace(f: pathlib.Path):
    if f.is_file():
        shutil.copyfile(f, workspace.joinpath(f.name))
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


def remove_workspace():
    if workspace.exists():
        shutil.rmtree(workspace)


def refresh_workspace():
    remove_workspace()
    workspace.mkdir()


def clear_cache():
    for cache_dir in [checkpointing_cache, cachier_cache, joblib_cache]:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)


def run_case(case_path: pathlib.Path):

    refresh_workspace()
    clear_cache()

    resource_path = case_path.joinpath("resources")

    if resource_path.exists():  # Resource setup
        for f in resource_path.iterdir():
            copy_file_to_workplace(f)

    for i in count():
        wspath = case_path.joinpath("workspaces", f"workspace{i}")
        outputpath = case_path.joinpath("outputs", f"output{i}.txt")

        if not wspath.exists():
            break

        for f in wspath.iterdir():  # Script setup
            copy_file_to_workplace(f)

        time.sleep(0.5) # Sometimes copy doesn't finish and it causes tests to fail randomly

        if not outputpath.exists():
            raise TestDefinitionError(f"Case {i} for {case_path} has script definition, but no expected output")

        with open(outputpath, mode="r", encoding="utf-8") as f:
            expected = sanitize(f.read())

        try:
            p = subprocess.run(
                ["python", "-m", f"{workspace.name}.main"],
                capture_output=True,
                check=True,
                cwd=cwd,
            )
        except subprocess.CalledProcessError as e:
            raise TestFailedError(f"Test failed in {case_path}, workspace{i} because an exception is raised.\n" + e.stdout + "\n" + e.stderr)

        actual = sanitize(p.stdout.decode("utf-8"))

        if expected != actual:
            raise TestFailedError(
                f"""Test failed in {case_path}, workspace{i} because the output does not match the expectation.
<Expected>
{expected}

<Actual>
{actual}
                """.strip()
            )

        for f in wspath.iterdir():  # Script teardown
            remove_file_in_workplace(f)

    if resource_path.exists():  # Resource teardown
        for f in resource_path.iterdir():
            remove_file_in_workplace(f)

    if i == 0:
        raise TestDefinitionError(f"No workspace exists for case {case_path}, at least 1 is expected.")


def is_case(d: pathlib.Path):
    for sub_d in d.iterdir():
        if sub_d.is_dir() and sub_d.name not in ["outputs", "workspaces", "__pycache__"]:
            return False

    return True


def find_cases():
    q = list(pathlib.Path(".").joinpath("integtests").iterdir())

    while q:
        d = q.pop()
        if d.is_dir() and d.name != "__pycache__":
            if is_case(d):
                yield d
            else:
                for sub_d in d.iterdir():
                    if sub_d.is_dir() and d.name != "__pycache__":
                        q.append(sub_d)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("keyword", nargs="?", type=str, help="Only run tests including this keyword", default=None)

    args = parser.parse_args()
    keyword = args.keyword

    cprint("Integration tests:")

    failed = []
    passed = 0

    for case in find_cases():

        cprint(f"Running case: {case}", end=" ")

        if keyword is not None and keyword not in str(case):
            cprint("Skipped", "blue")
            continue

        try:
            run_case(case)

        except TestDefinitionError as e:
            cprint(f"Definition Error: {e}", "red")
            failed.append(case)

        except TestFailedError as e:
            cprint(f"Failed: {e}", "red")
            failed.append(case)

        else:
            cprint("Passed", "green")
            passed += 1

    cprint(f"Total passed: {passed}", "green")
    if failed:
        cprint(f"Total failed: {len(failed)}", "red")
        cprint("Failed tests:", "red")
        cprint("\n".join([f"- {f}" for f in failed]), "red")

    remove_workspace()
    clear_cache()

    exit(len(failed))
