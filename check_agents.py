import os
HERE = os.path.dirname(os.path.abspath(__file__))
NEEDED = ["task.json", "tools.py", "state.json", "checks.py", "trace.jsonl", "run.py", "Rules", "Run:"]

def check():
    with open(os.path.join(HERE, "AGENTS.md")) as f:
        text = f.read()
    lines = text.strip().splitlines()
    missing = [w for w in NEEDED if w not in text]
    if len(lines) > 15:
        return False, f"{len(lines)} lines (max 15)"
    if missing:
        return False, f"missing {missing}"
    return True, f"{len(lines)} lines, map + rules + run steps present"

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
