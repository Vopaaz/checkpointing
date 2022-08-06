"""
Popping .../IPython/extensions from sys.path, otherwise the `import tests.xxx` statement 
will import that module within IPython instead. See https://github.com/ipython/ipython/issues/12892.
"""

import sys
import os

ext_path = None

for path in sys.path:
    if path.endswith(os.path.join("IPython", "extensions")):
        ext_path = path

if ext_path:
    sys.path.remove(ext_path)
