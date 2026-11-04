# ============================================================
#  DELETE everything in Code Pad before pasting this version.
#  stock-harness phone v9 - copy ALL of this, paste, tap Run.
#  Standard library only. Learning only, never trades.
# ============================================================
VERSION = "stock-harness phone v9 (9/9 sessions)"
print(VERSION)
print("=" * len(VERSION))

import os, tempfile

def _can_write(d):
    try:
        if not d or os.path.realpath(d) == os.path.realpath("/"):
            return False  # never write to "/"
        probe = os.path.join(d, ".sh_probe")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        return True
    except Exception:
        return False

def _pick_dir():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        here = None
    for d in (os.getcwd(), here, os.path.expanduser("~"), tempfile.gettempdir()):
        if _can_write(d):
            return d
    return None

WRITE_DIR = _pick_dir()
PHONE_MODE = "files in " + WRITE_DIR if WRITE_DIR else "memory-only"
print("Mode: " + PHONE_MODE + ("" if WRITE_DIR else " (this app can't save files; that's OK, everything runs in memory)"))
print()

TASK = {
    "goal": "Write a daily recap for NVDA, MSFT, VOO",
    "output": "report.md",
    "constraints": ["read-only", "no trades", "free data only"],
    "done_when": "report has all sections and passes checks",
}

AGENTS_MD = """# AGENTS.md - map of stock-harness (learning only, never trades)
Files: task.json = job card | tools.py = get_prices + write_report | state.json = memory
checks.py = freshness, sanity, sections | trace.jsonl = step log | run.py = whole loop + receipt
Rules: read-only; anything else needs a human "yes"; max 3 retries, then NEEDS HUMAN.
Permissions:
| Action | Allowed? |
|---|---|
| Read prices | Allowed |
| Write report.md (inside project only) | Allowed |
| Buy/sell, email, post | Needs approval (not built) |
Run: python run.py (phone: open run_on_phone.py and tap Run)
"""

def check_task(task):
    missing = [k for k in ["goal", "output", "constraints", "done_when"] if not task.get(k)]
    return (not missing, "all 4 fields present" if not missing else "missing %s" % missing)

def check_agents(text):
    needed = ["task.json", "tools.py", "state.json", "checks.py", "trace.jsonl", "run.py", "Rules", "Run:"]
    lines = text.strip().splitlines()
    missing = [w for w in needed if w not in text]
    if len(lines) > 15:
        return False, "%d lines (max 15)" % len(lines)
    if missing:
        return False, "missing %s" % missing
    return True, "%d lines, map + rules + run steps present" % len(lines)

# ---- Session 3: price tool (live data first, SAMPLE DATA if offline) ----
import json, urllib.request, datetime
OFFLINE_TEST = False  # set True to practice the offline fallback

SAMPLE_PRICES = {  # EXAMPLE values only. NOT real prices.
    "NVDA": {"close": 100.00, "prev_close": 99.00, "date": "2000-01-01"},
    "MSFT": {"close": 200.00, "prev_close": 198.00, "date": "2000-01-01"},
    "VOO":  {"close": 300.00, "prev_close": 297.00, "date": "2000-01-01"},
}

def _yf(t):
    if OFFLINE_TEST: raise ImportError("offline test")
    import yfinance as yf
    h = yf.Ticker(t).history(period="10d").dropna(subset=["Close"])
    if h.empty: raise ValueError("no data")
    prev = round(float(h["Close"].iloc[-2]), 2) if len(h) > 1 else None
    return {"close": round(float(h["Close"].iloc[-1]), 2), "prev_close": prev, "date": h.index[-1].strftime("%Y-%m-%d")}

def _chart(t):
    if OFFLINE_TEST: raise OSError("offline test")
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=10d&interval=1d" % t
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.load(r)["chart"]["result"][0]
    pts = [(a, c) for a, c in zip(res.get("timestamp") or [], res["indicators"]["quote"][0].get("close") or []) if c is not None]
    if not pts: raise ValueError("no data")
    a, c = pts[-1]
    prev = round(pts[-2][1], 2) if len(pts) > 1 else None
    return {"close": round(c, 2), "prev_close": prev, "date": datetime.datetime.fromtimestamp(a, datetime.timezone.utc).strftime("%Y-%m-%d")}

def get_prices(tickers):
    out, offline = {}, False
    for t in tickers:
        errs, bad_ticker = [], False
        for name, fn in (("live (yfinance)", _yf), ("live (Yahoo chart)", _chart)):
            try:
                out[t] = dict(fn(t), source=name); break
            except (ImportError, OSError) as e:
                if "404" in str(e): bad_ticker = True
                errs.append(name + ": " + str(e))
            except Exception as e:
                bad_ticker = True; errs.append(name + ": " + str(e))
        else:
            if t in SAMPLE_PRICES and not bad_ticker:
                out[t] = dict(SAMPLE_PRICES[t], source="SAMPLE DATA"); offline = True
            else:
                out[t] = {"error": "Could not get a price for %s (bad ticker or no data)" % t}
    return out, offline

LAST_SOURCE = {"offline": None}

def check_tools(_):
    r, offline = get_prices(["NVDA", "MSFT", "VOO", "ZZZZ"])
    for t in ["NVDA", "MSFT", "VOO"]:
        v = r[t]
        print("      %s: %s" % (t, "%.2f on %s [%s]" % (v["close"], v["date"], v["source"]) if "close" in v else v["error"]))
    print("      ZZZZ: " + r["ZZZZ"].get("error", "UNEXPECTED PRICE"))
    LAST_SOURCE["offline"] = offline
    ok = "close" in r["NVDA"] and "error" in r["ZZZZ"]
    return ok, ("SAMPLE DATA used (offline) - prices are NOT real" if offline else "live prices + clean ZZZZ error")

# ---- Session 4: write the report (show on screen, try to save) ----
def build_report(prices):
    sample = any("SAMPLE" in v.get("source", "") for v in prices.values())
    L = ["# Daily stock recap", "", "## Summary",
         "Recap for %s. %s" % (", ".join(prices), "SAMPLE DATA - prices are NOT real." if sample else "Live prices."),
         "", "## Prices"]
    for t, v in prices.items():
        if "close" in v:
            chg = " (%+.2f%% vs prev close)" % ((v["close"] / v["prev_close"] - 1) * 100) if v.get("prev_close") else ""
            L.append("- %s: $%.2f on %s%s [%s]" % (t, v["close"], v["date"], chg, v["source"]))
        else:
            L.append("- %s: %s" % (t, v["error"]))
    L += ["", "## Notes", "Free data can be late or missing. Checks run before this report is trusted.",
          "", "## Disclaimer", "Learning project only. Not financial advice. This tool never trades."]
    return "\n".join(L) + "\n"

def check_report(_):
    prices, offline = get_prices(["NVDA", "MSFT", "VOO"])
    text = build_report(prices)
    print("      ----- report.md -----")
    for line in text.splitlines():
        print("      " + line)
    if WRITE_DIR:
        try:
            with open(os.path.join(WRITE_DIR, "report.md"), "w") as f:
                f.write(text)
            saved = "saved report.md in " + WRITE_DIR
        except Exception as e:
            saved = "could not save (that's OK): %s" % e
    else:
        saved = "kept in memory (this app can't save files)"
    table = all(w in AGENTS_MD for w in ["Permissions", "Read prices", "Write report.md", "Needs approval"])
    return table and "## Prices" in text, saved + ("; permission table present" if table else "; permission table MISSING")

# ---- Session 5: state memory (decisions, failures, pending) ----
import json, datetime
KINDS = ("decisions", "failures", "pending")
_MEMORY = {}  # used when the app can't save files

def load_state(path):
    if path is None:
        s = json.loads(json.dumps(_MEMORY)) if _MEMORY else {}
    else:
        try:
            with open(path) as f:
                s = json.load(f)
        except (OSError, ValueError):
            s = {}
    for k in KINDS:
        s.setdefault(k, [])
    return s

def save_state(s, path):
    if path is None:
        _MEMORY.clear(); _MEMORY.update(json.loads(json.dumps(s)))
    else:
        with open(path, "w") as f:
            json.dump(s, f, indent=2)

def add(kind, text, path):
    s = load_state(path)
    s[kind].append({"time": datetime.datetime.now().isoformat(timespec="seconds"), "text": text})
    save_state(s, path)

def check_state(_):
    path = os.path.join(WRITE_DIR, "state.json") if WRITE_DIR else None
    tag = datetime.datetime.now().strftime("%H%M%S%f")
    src = "SAMPLE DATA (offline)" if LAST_SOURCE["offline"] else "live data"
    add("decisions", "used %s %s" % (src, tag), path)
    add("failures", "ZZZZ had no data %s" % tag, path)
    add("pending", "ask Aaron which tickers to add %s" % tag, path)
    s = load_state(path)  # reload from scratch
    found = [k for k in KINDS if any(tag in e["text"] for e in s[k])]
    for k in KINDS:
        print("      %s: %s" % (k, s[k][-1]["text"]))
    where = ("reloaded from " + path) if path else "memory-only mode: added and reloaded in memory (won't survive closing the app)"
    return len(found) == 3, "%d/3 entries; %s" % (len(found), where)

# ---- Session 6: checks (freshness, sanity, required sections) ----
REQUIRED_SECTIONS = ["## Summary", "## Prices", "## Notes", "## Disclaimer"]

def check_freshness(prices, today=None, max_days=4):
    today = today or datetime.date.today()
    stale = ["%s is %d days old" % (t, (today - datetime.date.fromisoformat(v["date"])).days)
             for t, v in prices.items() if "date" in v and (today - datetime.date.fromisoformat(v["date"])).days > max_days]
    return (not stale, "all prices within %d days" % max_days if not stale else "STALE: " + "; ".join(stale))

def check_sanity(prices, max_move=0.50):
    bad = []
    for t, v in prices.items():
        if "close" not in v: continue
        c, p = v["close"], v.get("prev_close")
        if not c > 0: bad.append("%s price %s is not above 0" % (t, c))
        elif p and abs(c / p - 1) > max_move: bad.append("%s moved %.0f%% from prev close" % (t, (c / p - 1) * 100))
    return (not bad, "prices look sane" if not bad else "INSANE: " + "; ".join(bad))

def check_sections(text):
    missing = [x[3:] for x in REQUIRED_SECTIONS if x not in text]
    return (not missing, "all 4 sections present" if not missing else "MISSING: " + ", ".join(missing))

def check_checks(_):
    today = datetime.date(2026, 11, 3)
    good = {"NVDA": {"close": 206.69, "prev_close": 202.06, "date": "2026-11-03", "source": "test"}}
    tests = [("good data: freshness", check_freshness(good, today), True),
             ("good data: sanity", check_sanity(good), True),
             ("good data: sections", check_sections(build_report(good)), True),
             ("fake stale date", check_freshness({"X": {"close": 1, "date": "2026-10-20"}}, today), False),
             ("fake zero price", check_sanity({"X": {"close": 0}}), False),
             ("fake 60% jump", check_sanity({"X": {"close": 160, "prev_close": 100}}), False),
             ("fake missing sections", check_sections("## Prices"), False)]
    wrong = [n for n, (ok, _), want in tests if ok != want]
    print("      Self-test: %d/%d checks behaved correctly" % (len(tests) - len(wrong), len(tests)))
    prices, offline = get_prices(["NVDA", "MSFT", "VOO"])
    text = build_report(prices)
    f_ok, f_msg = check_freshness(prices)
    s_ok, s_msg = check_sanity(prices)
    x_ok, x_msg = check_sections(text)
    print("      Today's data: freshness -> %s" % f_msg)
    if offline and not f_ok:
        print("        ^ EXPECTED: SAMPLE DATA is dated 2000, so freshness should fail. This is the check working.")
    print("      Today's data: sanity -> %s" % s_msg)
    print("      Today's data: sections -> %s" % x_msg)
    fresh_right = (not f_ok) if offline else f_ok
    ok = not wrong and fresh_right and s_ok and x_ok
    return ok, "self-test %d/%d; %s" % (len(tests) - len(wrong), len(tests),
           "SAMPLE DATA failed freshness as expected" if offline else "live data passed all 3 checks")

QUIET = True  # one line per session; set False to see every detail

# ---- Session 7: approval gate (only a typed "yes" lets an action run) ----
def approve(action, ask=input, path=None):
    print("      APPROVAL NEEDED: " + action)
    try:
        answer = ask("      Type yes to allow, or no to block: ")
    except (EOFError, OSError, RuntimeError, KeyboardInterrupt) as e:
        add("failures", "BLOCKED '%s': no input (%s), safe NO" % (action, type(e).__name__), path)
        return False, "typing not available here (%s) - safe default NO" % type(e).__name__
    if answer.strip().lower() == "yes":
        add("decisions", "APPROVED '%s'" % action, path)
        return True, "you typed yes"
    add("failures", "BLOCKED '%s': answered %r" % (action, answer), path)
    return False, "you typed %r, so it was blocked" % answer

def fake_send_email(text):
    print("      [FAKE] Would email the report (%d chars). Nothing was sent." % len(text))
    return "fake-sent"

def check_approval(_):
    path = os.path.join(WRITE_DIR, "state.json") if WRITE_DIR else None
    def no_input(p=""): raise EOFError
    # Self-test with simulated answers (no typing needed)
    t_yes = approve("SIMULATED test (no typing needed)", lambda p="": "yes", path)[0]
    t_no = approve("SIMULATED test (no typing needed)", lambda p="": "no", path)[0]
    t_none = approve("SIMULATED test (no typing needed)", no_input, path)[0]
    selftest = t_yes and not t_no and not t_none
    print("      Self-test: yes -> allowed, no -> blocked, no input -> blocked: %s" % ("OK" if selftest else "WRONG"))
    # The real one: Aaron decides
    if QUIET:
        return selftest, "yes/no/no-input simulated OK (real question comes in Session 9)"
    ok, msg = approve("send report by email (FAKE - only prints)", input, path)
    if ok:
        fake_send_email("report")
        print("      RESULT: approved. The fake action ran (still nothing sent).")
    else:
        print("      RESULT: STOPPED - " + msg + ". Refusal logged to state.")
    return selftest, "self-test OK; your answer: " + ("yes (fake action ran)" if ok else "blocked (" + msg + ")")

# ---- Session 8: trace log, 3-try retry cap, escalation ----
import time
TRACE_MEMORY = []
MAX_TRIES = 3

def trace(step, result):
    line = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "step": step, "result": result}
    TRACE_MEMORY.append(line)
    if WRITE_DIR:
        try:
            with open(os.path.join(WRITE_DIR, "trace.jsonl"), "a") as f:
                f.write(json.dumps(line) + "\n")
        except Exception:
            pass

def fetch_live_only(tickers):
    out = {}
    for t in tickers:
        try:
            out[t] = dict(_chart(t), source="live (Yahoo chart)")
        except Exception as e:
            out[t] = {"error": str(e)}
    if not any("close" in v for v in out.values()):
        raise OSError("no live prices (offline?)")
    return out

def fetch_with_retry(fetch, tickers, wait=0.5, sleep=time.sleep):
    last = None
    for attempt in range(1, MAX_TRIES + 1):
        try:
            prices = fetch(tickers)
            trace("fetch attempt %d" % attempt, "ok")
            print("      try %d/%d: ok" % (attempt, MAX_TRIES))
            return prices, attempt
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, e)
        trace("fetch attempt %d" % attempt, "failed: " + last)
        print("      try %d/%d failed: %s" % (attempt, MAX_TRIES, last))
        if attempt < MAX_TRIES:
            sleep(wait)
    path = os.path.join(WRITE_DIR, "state.json") if WRITE_DIR else None
    add("pending", "NEEDS HUMAN: price fetch failed %d times (%s)" % (MAX_TRIES, last), path)
    trace("escalate", "NEEDS HUMAN")
    print("      NEEDS HUMAN: price fetch failed %d times. Logged to pending." % MAX_TRIES)
    return None, MAX_TRIES

def check_trace(_):
    # Self-test: fake outage must give exactly 3 tries, then escalate
    calls = {"n": 0}
    def outage(t):
        calls["n"] += 1; raise OSError("fake outage (simulated)")
    print("      SIMULATED outage test:")
    r, _ = fetch_with_retry(outage, ["NVDA"], wait=0, sleep=lambda s: None)
    selftest = r is None and calls["n"] == 3 and TRACE_MEMORY[-1]["result"] == "NEEDS HUMAN"
    print("      Self-test: %d tries then escalate: %s" % (calls["n"], "OK" if selftest else "WRONG"))
    # Real fetch
    print("      Real fetch:")
    prices, tries = fetch_with_retry(lambda t: fetch_live_only(t) if not OFFLINE_TEST else (_ for _ in ()).throw(OSError("offline test")), ["NVDA", "MSFT", "VOO"])
    if prices is None:
        prices = {t: dict(v, source="SAMPLE DATA") for t, v in SAMPLE_PRICES.items()}
        trace("fallback", "continued with SAMPLE DATA")
        print("      Continuing with SAMPLE DATA (prices are NOT real).")
    print("      Last trace lines:")
    for line in TRACE_MEMORY[-4:]:
        print("        " + json.dumps(line))
    how = ("live prices on try %d" % tries) if "SAMPLE" not in list(prices.values())[0]["source"] else "3 tries, NEEDS HUMAN, then SAMPLE DATA"
    return selftest, "self-test OK; real run: " + how

# ---- Session 9: the whole loop in one run, plus a receipt ----
def full_run():
    print("----- FULL RUN (Session 9) -----")
    start = datetime.datetime.now()
    path = os.path.join(WRITE_DIR, "state.json") if WRITE_DIR else None
    tickers = ["NVDA", "MSFT", "VOO"]
    trace("start", "task: " + TASK["goal"])
    print("Task: " + TASK["goal"])
    n = {"tries": 0}
    def fetch(t):
        n["tries"] += 1
        if OFFLINE_TEST: raise OSError("offline test")
        return fetch_live_only(t)
    prices, _ = fetch_with_retry(fetch, tickers)
    sample = prices is None
    if sample:
        prices = {t: dict(v, source="SAMPLE DATA") for t, v in SAMPLE_PRICES.items()}
        print("      Continuing with SAMPLE DATA (prices are NOT real).")
    add("decisions", "full run used " + ("SAMPLE DATA" if sample else "live data"), path)
    text = build_report(prices)
    saved = "memory only"
    if WRITE_DIR:
        try:
            with open(os.path.join(WRITE_DIR, "report.md"), "w") as f: f.write(text)
            saved = "report.md saved"
        except Exception: pass
    trace("write_report", saved)
    res = {"freshness": check_freshness(prices), "sanity": check_sanity(prices), "sections": check_sections(text)}
    for k, (ok, m) in res.items():
        trace("check " + k, ("pass: " if ok else "FAIL: ") + m)
    ok_checks = all(ok for ok, _ in res.values())
    expected_only = sample and not res["freshness"][0] and res["sanity"][0] and res["sections"][0]
    approvals = []
    if ok_checks or expected_only:
        approved, msg = approve("send report by email (FAKE - only prints)", input, path)
        if approved: fake_send_email(text)
        else: print("      STOPPED - " + msg)
        approvals.append(("send report by email (FAKE)", "approved" if approved else "blocked"))
    status = "DONE" if ok_checks else ("DONE with SAMPLE DATA (freshness failed as expected)" if expected_only else "CHECKS FAILED")
    receipt = {"start": start.strftime("%H:%M:%S"), "end": datetime.datetime.now().strftime("%H:%M:%S"),
               "tickers": tickers, "data": "SAMPLE DATA (not real)" if sample else "live",
               "fetch_tries": n["tries"], "checks": res, "approvals": approvals, "status": status, "saved": saved}
    if WRITE_DIR:
        try:
            with open(os.path.join(WRITE_DIR, "receipt.json"), "w") as f: json.dump(receipt, f, indent=2, default=str)
        except Exception: pass
    trace("finish", status)
    print()
    print("=========== RUN RECEIPT ===========")
    print("Task:        " + TASK["goal"])
    print("Time:        %s -> %s" % (receipt["start"], receipt["end"]))
    print("Data:        %s (%d fetch %s)" % (receipt["data"], n["tries"], "try" if n["tries"] == 1 else "tries"))
    for t, v in prices.items():
        if "close" in v: print("  %-5s $%.2f on %s" % (t, v["close"], v["date"]))
    for k, (ok, m) in res.items():
        tag = "PASS" if ok else ("FAIL (expected)" if sample and k == "freshness" else "FAIL")
        print("Check %-10s %s" % (k + ":", tag))
    for a, r in approvals: print("Approval:    %s -> %s" % (a, r))
    print("Saved:       " + saved)
    print("Status:      " + status)
    print("Learning only. Never trades. Not financial advice.")
    print("===================================")
    return ok_checks or expected_only, status

def check_full(_):
    return True, "see receipt below"

import io, contextlib
results = []
for name, fn, arg in [("Session 1 - task contract", check_task, TASK),
                      ("Session 2 - AGENTS.md map", check_agents, AGENTS_MD),
                      ("Session 3 - price tool", check_tools, None),
                      ("Session 4 - report + permissions", check_report, None),
                      ("Session 5 - state memory", check_state, None),
                      ("Session 6 - checks", check_checks, None),
                      ("Session 7 - approval gate", check_approval, None),
                      ("Session 8 - trace + retries", check_trace, None)]:
    try:
        if QUIET:
            with contextlib.redirect_stdout(io.StringIO()):
                ok, msg = fn(arg)
        else:
            ok, msg = fn(arg)
    except Exception as e:
        ok, msg = False, "error: %s" % e
    results.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ": " + msg[:90])
print()
try:
    ok9, status9 = full_run()
except Exception as e:
    ok9, status9 = False, "error: %s" % e
results.append(ok9)
print()
print(("PASS  " if ok9 else "FAIL  ") + "Session 9 - full run + receipt: " + status9)
print()
if all(results):
    print("All good! %d/%d sessions pass." % (sum(results), len(results)))
else:
    print("Something needs fixing: %d/%d pass." % (sum(results), len(results)))
