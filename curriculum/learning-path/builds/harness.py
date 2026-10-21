import ast, json, os, sys, traceback

# os._exit() would stop Python itself and look like a broken runner. In the student's code it raises SystemExit.
def __exit_now(code=0):
    raise SystemExit(code)

os._exit = __exit_now

def __coverage_map(student):
    """Lines and branches of the code under test: every function in your_code.py whose name does not start with test_."""
    tree = ast.parse(student)
    lines, branches = set(), {}
    src = student.split("\n")
    for f in ast.walk(tree):
        if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) or f.name.startswith("test_"):
            continue
        for n in ast.walk(f):
            if n is f or isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(n, ast.stmt) and not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant) and isinstance(n.value.value, str)):
                lines.add(n.lineno)
            if isinstance(n, (ast.If, ast.While, ast.For)) and n.body and n.body[0].lineno != n.lineno:
                text = src[n.lineno - 1].strip()
                if isinstance(n, ast.If):
                    other = n.orelse[0].lineno if n.orelse else None
                    branches[n.lineno] = [text, n.body[0].lineno, other, "true", "false"]
                else:
                    branches[n.lineno] = [text, n.body[0].lineno, None, "loop body runs", "loop is skipped or ends"]
    return lines, branches

def __tracer(hit, arcs):
    def call(frame, event, arg):
        code = frame.f_code
        if code.co_filename != "your_code.py" or code.co_name.startswith("test_") or code.co_name == "<module>":
            return None
        last = [None]
        def local(frame, event, arg):
            if event == "line":
                hit.add(frame.f_lineno); arcs.add((last[0], frame.f_lineno)); last[0] = frame.f_lineno
            elif event == "return":
                arcs.add((last[0], -1))
            return local
        return local
    return call

def __coverage(student, hit, arcs):
    try:
        lines, branches = __coverage_map(student)
    except BaseException:
        return None
    rows = []
    for line in sorted(branches):
        text, first, other, yes, no = branches[line]
        took_yes = (line, first) in arcs
        took_no = (line, other) in arcs if other else any(a == line and b != first for a, b in arcs)
        rows.append([line, text[:70], yes, took_yes, no, took_no])
    return {"lines": [len(lines & hit), len(lines)], "missed": sorted(lines - hit),
            "branches": [sum(r[3] + r[5] for r in rows), 2 * len(rows)], "rows": rows}

def __last_line(e):
    return type(e).__name__ + (": " + str(e) if str(e) else "")

def __mutate(helpers, student, mutants, tests):
    """Run your tests against known buggy versions. A bug is caught when at least one test fails."""
    spec = {}
    exec(mutants, spec)
    res = []
    for label, code in spec["MUTANTS"]:
        mns = {"__name__": "student"}
        try:
            exec(helpers, mns)
            exec(compile(student, "your_code.py", "exec"), mns)
            exec(code, mns)
        except BaseException:
            res.append([label, True]); continue
        killed = False
        for name in tests:
            try:
                mns[name]()
            except BaseException:
                killed = True
                break
        res.append([label, killed])
    return res

def __run(helpers, student, checks, mutants=""):
    ns = {"__name__": "student"}
    out = {"tests": [], "checks": [], "error": None}
    try:
        exec(helpers, ns)
    except BaseException as e:
        out["error"] = "Course helpers failed: " + __last_line(e)
        return json.dumps(out)
    base = dict(ns)   # the checks use the very same helper classes as the student code
    try:
        exec(compile(student, "your_code.py", "exec"), ns)
    except SyntaxError as e:
        out["error"] = f"Your code did not run (line {e.lineno}): SyntaxError: {e.msg}"
        return json.dumps(out)
    except BaseException as e:
        tb = traceback.extract_tb(e.__traceback__)
        line = next((f.lineno for f in reversed(tb) if f.filename == "your_code.py"), None)
        out["error"] = "Your code did not run" + (f" (line {line})" if line else "") + ": " + __last_line(e)
        return json.dumps(out)
    ns["__source__"] = student
    hit, arcs = set(), set()
    for name in sorted(k for k, v in list(ns.items()) if k.startswith("test_") and callable(v)):
        sys.settrace(__tracer(hit, arcs))   # coverage counts only what your own tests run
        try:
            ns[name]()
            out["tests"].append([name, True, ""])
        except AssertionError as e:
            out["tests"].append([name, False, "assertion failed" + (": " + str(e) if str(e) else "")])
        except BaseException as e:
            out["tests"].append([name, False, __last_line(e)])
        finally:
            sys.settrace(None)
    cov = __coverage(student, hit, arcs)
    if (not cov or not cov["lines"][1]) and callable(ns.get("_tree_coverage")):
        try:
            cov = ns["_tree_coverage"](ns)   # a build without functions (the fault tree) measures its gates instead
        except BaseException:
            pass
    out["coverage"] = cov
    cns = dict(base)
    cns["__name__"] = "checks"
    exec(checks, cns)
    def own_tests(ns, out):
        t = out["tests"]
        assert len(t) >= 3, f"write at least three test_ functions (found {len(t)})"
        bad = [n for n, ok, _ in t if not ok]
        assert not bad, "failing: " + ", ".join(bad)
    extra = [("your own tests: at least three, all passing", own_tests)]
    if mutants:
        out["mutants"] = __mutate(helpers, student, mutants, [t[0] for t in out["tests"]])
        def catches(ns, out):
            assert out["tests"] and all(ok for _, ok, _ in out["tests"]), "first make your own tests pass on your code"
            missed = [m for m, killed in out["mutants"] if not killed]
            assert not missed, f"your tests catch {len(out['mutants']) - len(missed)} of {len(out['mutants'])} known bugs; not caught: " + "; ".join(missed)
        extra.append(("your tests catch every known bug (mutation test)", catches))
    for label, fn in cns["CHECKS"] + extra:
        try:
            fn(ns, out)
            out["checks"].append([label, True, ""])
        except AssertionError as e:
            out["checks"].append([label, False, str(e) or "not met"])
        except BaseException as e:
            out["checks"].append([label, False, "your code raised " + __last_line(e)])
    return json.dumps(out)

def __their(helpers, student, their):
    """Run 3 · their change: a part you did not write changes; your code and tests stay as they are."""
    ns = {"__name__": "student"}
    out = {"tests": [], "evidence": [], "correct": None, "error": None}
    tns = {"__name__": "their"}
    try:
        exec(helpers, ns)
        exec(their, tns)
        tns["install"](ns)
        exec(compile(student, "your_code.py", "exec"), ns)
    except BaseException as e:
        out["error"] = "Your code did not run: " + __last_line(e)
        return json.dumps(out)
    for name in sorted(k for k, v in list(ns.items()) if k.startswith("test_") and callable(v)):
        try:
            ns[name]()
            out["tests"].append([name, True, ""])
        except AssertionError as e:
            out["tests"].append([name, False, "assertion failed" + (": " + str(e) if str(e) else "")])
        except BaseException as e:
            out["tests"].append([name, False, __last_line(e)])
    try:
        lines, correct = tns["scenario"](ns)
        out["evidence"], out["correct"] = [str(x) for x in lines], bool(correct)
    except BaseException as e:
        out["evidence"], out["correct"] = ["your code raised " + __last_line(e) + " on the shared case"], False
    return json.dumps(out)
