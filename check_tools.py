import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import get_prices

def check():
    r = get_prices(["NVDA", "ZZZZ"])
    real_ok = "close" in r["NVDA"] and r["NVDA"]["close"] > 0
    bad_ok = "error" in r["ZZZZ"]
    if real_ok and bad_ok:
        return True, "NVDA %s on %s via %s; ZZZZ -> clean error" % (r["NVDA"]["close"], r["NVDA"]["date"], r["NVDA"]["source"])
    return False, "NVDA=%s ZZZZ=%s" % (r["NVDA"], r["ZZZZ"])

if __name__ == "__main__":
    ok, msg = check(); print(("PASS: " if ok else "FAIL: ") + msg)
