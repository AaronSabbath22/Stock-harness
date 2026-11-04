import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tools import write_report

def check():
    ok1, m1 = write_report("# Test report\nLearning only.\n")
    exists = os.path.exists(os.path.join(HERE, "report.md"))
    ok2, m2 = write_report("x", "../escape.md")
    ok3, m3 = write_report("x", "/tmp/escape.md")
    with open(os.path.join(HERE, "AGENTS.md")) as f:
        agents = f.read()
    table = all(w in agents for w in ["Permissions", "Read prices", "Write report.md", "Needs approval"])
    ok = ok1 and exists and not ok2 and not ok3 and table
    return ok, "%s; ../escape.md -> %s; /tmp/escape.md -> %s; permission table %s" % (m1, m2, m3, "present" if table else "MISSING")

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
