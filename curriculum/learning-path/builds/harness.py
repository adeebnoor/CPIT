import json, traceback

def __last_line(e):
    return type(e).__name__ + (": " + str(e) if str(e) else "")

def __run(helpers, student, checks):
    ns = {"__name__": "student"}
    out = {"tests": [], "checks": [], "error": None}
    try:
        exec(helpers, ns)
    except Exception as e:
        out["error"] = "Course helpers failed: " + __last_line(e)
        return json.dumps(out)
    base = dict(ns)   # the checks use the very same helper classes as the student code
    try:
        exec(compile(student, "your_code.py", "exec"), ns)
    except SyntaxError as e:
        out["error"] = f"Your code did not run (line {e.lineno}): SyntaxError: {e.msg}"
        return json.dumps(out)
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line = next((f.lineno for f in reversed(tb) if f.filename == "your_code.py"), None)
        out["error"] = "Your code did not run" + (f" (line {line})" if line else "") + ": " + __last_line(e)
        return json.dumps(out)
    ns["__source__"] = student
    for name in sorted(k for k, v in list(ns.items()) if k.startswith("test_") and callable(v)):
        try:
            ns[name]()
            out["tests"].append([name, True, ""])
        except AssertionError as e:
            out["tests"].append([name, False, "assertion failed" + (": " + str(e) if str(e) else "")])
        except Exception as e:
            out["tests"].append([name, False, __last_line(e)])
    cns = dict(base)
    cns["__name__"] = "checks"
    exec(checks, cns)
    def own_tests(ns, out):
        t = out["tests"]
        assert len(t) >= 3, f"write at least three test_ functions (found {len(t)})"
        bad = [n for n, ok, _ in t if not ok]
        assert not bad, "failing: " + ", ".join(bad)
    for label, fn in cns["CHECKS"] + [("your own tests: at least three, all passing", own_tests)]:
        try:
            fn(ns, out)
            out["checks"].append([label, True, ""])
        except AssertionError as e:
            out["checks"].append([label, False, str(e) or "not met"])
        except Exception as e:
            out["checks"].append([label, False, "your code raised " + __last_line(e)])
    return json.dumps(out)
