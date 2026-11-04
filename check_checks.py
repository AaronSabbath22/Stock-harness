import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checks
from tools import build_report

def check():
    today = datetime.date(2026, 11, 3)
    good = {"NVDA": {"close": 206.69, "prev_close": 202.06, "date": "2026-11-03", "source": "test"}}
    tests = [
        ("good freshness", checks.check_freshness(good, today), True),
        ("good sanity", checks.check_sanity(good), True),
        ("good sections", checks.check_sections(build_report(good)), True),
        ("stale date", checks.check_freshness({"X": {"close": 1, "date": "2026-10-20"}}, today), False),
        ("zero price", checks.check_sanity({"X": {"close": 0, "date": "2026-11-03"}}), False),
        ("60% jump", checks.check_sanity({"X": {"close": 160, "prev_close": 100}}), False),
        ("missing sections", checks.check_sections("## Prices\n- X: $1"), False),
    ]
    wrong = [n for n, (ok, _), want in tests if ok != want]
    for n, (ok, msg), want in tests:
        print("      %-17s -> %s (%s)" % (n, "pass" if ok else "fail", msg))
    return (not wrong, "%d/%d checks behaved correctly" % (len(tests) - len(wrong), len(tests)) + ("" if not wrong else "; WRONG: %s" % wrong))

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
