"""state.py - Session 5: the agent's memory (decisions, failures, pending). Learning only."""
import json, os, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
KINDS = ("decisions", "failures", "pending")

def load_state(path=STATE_FILE):
    try:
        with open(path) as f:
            s = json.load(f)
    except (FileNotFoundError, ValueError):
        s = {}
    for k in KINDS:
        s.setdefault(k, [])
    return s

def save_state(s, path=STATE_FILE):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=2)
    os.replace(tmp, path)  # write-then-swap so a crash never leaves half a file

def add(kind, text, path=STATE_FILE):
    if kind not in KINDS:
        raise ValueError("kind must be one of %s" % (KINDS,))
    s = load_state(path)
    s[kind].append({"time": datetime.datetime.now().isoformat(timespec="seconds"), "text": text})
    save_state(s, path)
    return s

def add_decision(text, path=STATE_FILE): return add("decisions", text, path)
def add_failure(text, path=STATE_FILE): return add("failures", text, path)
def add_pending(text, path=STATE_FILE): return add("pending", text, path)
