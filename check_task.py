import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
REQUIRED = ["goal", "output", "constraints", "done_when"]

def check():
    with open(os.path.join(HERE, "task.json")) as f:
        task = json.load(f)
    missing = [k for k in REQUIRED if not task.get(k)]
    return (not missing, "all 4 fields present" if not missing else f"missing {missing}")

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
