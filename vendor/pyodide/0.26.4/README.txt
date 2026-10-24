Pyodide 0.26.4 core files, copied unchanged from https://cdn.jsdelivr.net/pyodide/v0.26.4/full/
(Pyodide is licensed under the Mozilla Public License 2.0: https://github.com/pyodide/pyodide).

The Python build runner loads Python from the CDN first. When that download fails, for example on a
blocked or unstable network, it loads these files from this site instead. See tools/apply_runner_fallback.py.

python_stdlib.dat: the bytes of python_stdlib.zip, each XOR 90. The runner uses it as a third source when python_stdlib.zip is blocked on the device (tools/apply_runner_stdlib.py).
