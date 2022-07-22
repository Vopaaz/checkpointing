
??? info "How the cases are written"

    The cases are generally written in the following format of two tabs.

    === "1st run"

        ```python title="script.py"
        def foo():
            print("Output before the code change")

        if __name__ == "__main__":
            foo()
        ```

        ```text title="Output"
        Output before the code change
        ```

    === "2nd run"

        ```python title="script.py"
        def foo():
            print("Output after the code change")

        if __name__ == "__main__":
            foo()
        ```

        ```text title="Output"
        Output after the code change
        ```

    This denotes:

    - At first, you have the script in the "1st run" tab.
      Running it gives you the corresponding output.
    - Next you modify the script and change it to what's shown in the "2nd run" tab.
      Running it gives you another result,
      and it shows how the function gets skipped or re-executed.
