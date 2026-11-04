"""checks.py - Session 6: catch bad output before trusting it. Each check returns (ok, message)."""
import datetime
REQUIRED_SECTIONS = ["## Summary", "## Prices", "## Notes", "## Disclaimer"]

def check_freshness(prices, today=None, max_days=4):
    today = today or datetime.date.today()
    stale = []
    for t, v in prices.items():
        if "date" not in v:
            continue
        age = (today - datetime.date.fromisoformat(v["date"])).days
        if age > max_days:
            stale.append("%s is %d days old" % (t, age))
    return (not stale, "all prices within %d days" % max_days if not stale else "STALE: " + "; ".join(stale))

def check_sanity(prices, max_move=0.50):
    bad = []
    for t, v in prices.items():
        if "close" not in v:
            continue
        c, p = v["close"], v.get("prev_close")
        if not c > 0:
            bad.append("%s price %s is not above 0" % (t, c))
        elif p and abs(c / p - 1) > max_move:
            bad.append("%s moved %.0f%% from prev close" % (t, (c / p - 1) * 100))
    return (not bad, "prices look sane" if not bad else "INSANE: " + "; ".join(bad))

def check_sections(text):
    missing = [s[3:] for s in REQUIRED_SECTIONS if s not in text]
    return (not missing, "all 4 sections present" if not missing else "MISSING sections: " + ", ".join(missing))

def run_all(prices, text, today=None):
    return {"freshness": check_freshness(prices, today), "sanity": check_sanity(prices), "sections": check_sections(text)}
