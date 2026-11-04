import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approval, state

def _no_input(prompt=""):
    raise EOFError

def check():
    path = os.path.join(tempfile.mkdtemp(), "state.json")
    r_yes = approval.send_report_by_email("report", lambda p="": "yes", path)
    r_no = approval.send_report_by_email("report", lambda p="": "no", path)
    r_none = approval.send_report_by_email("report", _no_input, path)
    s = state.load_state(path)
    blocked = [e for e in s["failures"] if "BLOCKED" in e["text"]]
    ok = r_yes == "fake-sent" and r_no is None and r_none is None and len(blocked) == 2
    return ok, "yes -> %s; no -> %s; no input -> %s; %d refusals logged" % (r_yes, r_no, r_none, len(blocked))

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
