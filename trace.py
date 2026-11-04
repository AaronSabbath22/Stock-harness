"""trace.py - Session 8: step log, retry cap, escalation. Learning only."""
import json, os, sys, time, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import state
TRACE_FILE = os.path.join(HERE, "trace.jsonl")
MAX_TRIES = 3

def log(step, result, path=TRACE_FILE):
    line = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "step": step, "result": result}
    with open(path, "a") as f:
        f.write(json.dumps(line) + "\n")
    return line

def fetch_with_retry(fetch, tickers, wait=2, sleep=time.sleep, trace_path=TRACE_FILE, state_path=state.STATE_FILE):
    """Try fetch(tickers) up to 3 times. Returns prices, or None after escalating to a human."""
    last = None
    for attempt in range(1, MAX_TRIES + 1):
        try:
            prices = fetch(tickers)
            if any("close" in v for v in prices.values()):
                log("fetch attempt %d" % attempt, "ok", trace_path)
                return prices
            last = "no prices returned"
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, e)
        log("fetch attempt %d" % attempt, "failed: " + last, trace_path)
        print("  try %d/%d failed: %s" % (attempt, MAX_TRIES, last))
        if attempt < MAX_TRIES:
            sleep(wait)
    state.add_pending("NEEDS HUMAN: price fetch failed %d times (%s)" % (MAX_TRIES, last), state_path)
    log("escalate", "NEEDS HUMAN", trace_path)
    print("NEEDS HUMAN: price fetch failed %d times. Stopping." % MAX_TRIES)
    return None
