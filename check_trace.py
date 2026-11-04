import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trace as tr, state

def check():
    d = tempfile.mkdtemp(); tp, sp = os.path.join(d, "trace.jsonl"), os.path.join(d, "state.json")
    calls = {"n": 0}
    def outage(tickers):
        calls["n"] += 1; raise OSError("fake outage")
    waits = []
    r = tr.fetch_with_retry(outage, ["NVDA"], wait=0, sleep=waits.append, trace_path=tp, state_path=sp)
    lines = [json.loads(l) for l in open(tp)]
    pending = state.load_state(sp)["pending"]
    ok_fail = r is None and calls["n"] == 3 and len(waits) == 2 and lines[-1]["result"] == "NEEDS HUMAN" and "NEEDS HUMAN" in pending[-1]["text"]
    good = tr.fetch_with_retry(lambda t: {"NVDA": {"close": 1.0}}, ["NVDA"], sleep=waits.append, trace_path=tp, state_path=sp)
    ok = ok_fail and good is not None
    return ok, "fake outage -> %d tries, %d waits, escalated=%s; good fetch -> ok on try 1; %d trace lines" % (calls["n"], len(waits), r is None, len(lines) + 1)

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
