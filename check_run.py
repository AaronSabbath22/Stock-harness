import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))

def check():
    for f in ("report.md", "receipt.json"):
        p = os.path.join(HERE, f)
        if os.path.exists(p): os.remove(p)
    subprocess.run([sys.executable, os.path.join(HERE, "run.py")], input="no\n", text=True, capture_output=True, timeout=180)
    has_report = os.path.exists(os.path.join(HERE, "report.md"))
    rp = os.path.join(HERE, "receipt.json")
    if not os.path.exists(rp):
        return False, "no receipt.json"
    r = json.load(open(rp))
    checks_ok = r.get("checks") and all(c["passed"] for c in r["checks"].values())
    ok = has_report and checks_ok and r["status"] == "DONE"
    return ok, "status %s; report.md %s; checks %s; tries %s" % (r["status"], "yes" if has_report else "no",
             ", ".join("%s=%s" % (k, "pass" if c["passed"] else "FAIL") for k, c in r.get("checks", {}).items()), r["fetch_tries"])

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
