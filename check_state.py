import os, sys, subprocess, tempfile, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

def check():
    tag = uuid.uuid4().hex[:6]
    path = os.path.join(tempfile.mkdtemp(), "state.json")
    # Run 1: a separate Python process adds entries, then exits (a "restart").
    code = ("import sys; sys.path.insert(0, %r); import state as s; "
            "s.add_decision('used yfinance %s', %r); s.add_failure('ZZZZ had no data %s', %r); "
            "s.add_pending('ask Aaron about tickers %s', %r)") % (HERE, tag, path, tag, path, tag, path)
    subprocess.run([sys.executable, "-c", code], check=True)
    # Run 2: a fresh process reloads it.
    import state
    s = state.load_state(path)
    found = [k for k in state.KINDS if any(tag in e["text"] for e in s[k])]
    ok = len(found) == 3
    return ok, "after restart, reloaded %d/3 entries (%s)" % (len(found), ", ".join(found))

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
