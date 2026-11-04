"""tools.py - Session 3: read-only price tool. Learning only, never trades."""
import csv, io, json, urllib.request, datetime

# Clearly labeled EXAMPLE values for offline practice. NOT real prices.
SAMPLE_PRICES = {
    "NVDA": {"close": 100.00, "prev_close": 99.00, "date": "2000-01-01"},
    "MSFT": {"close": 200.00, "prev_close": 198.00, "date": "2000-01-01"},
    "VOO":  {"close": 300.00, "prev_close": 297.00, "date": "2000-01-01"},
}

def _yahoo(t):
    import yfinance as yf
    h = yf.Ticker(t).history(period="10d")
    h = h.dropna(subset=["Close"]) if h is not None else h
    if h is None or h.empty:
        raise ValueError("no data (bad ticker or empty data)")
    prev = round(float(h["Close"].iloc[-2]), 2) if len(h) > 1 else None
    return {"close": round(float(h["Close"].iloc[-1]), 2), "prev_close": prev, "date": h.index[-1].strftime("%Y-%m-%d")}

def _yahoo_chart(t):
    """Standard-library only (works on a phone): Yahoo's free public chart endpoint."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=10d&interval=1d" % t
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.load(r)["chart"]["result"][0]
    except Exception as e:
        raise ValueError("no data (bad ticker, empty data, or no internet: %s)" % e)
    pts = [(ts, c) for ts, c in zip(res.get("timestamp") or [], res["indicators"]["quote"][0].get("close") or []) if c is not None]
    if not pts:
        raise ValueError("no data (bad ticker or empty data)")
    ts, c = pts[-1]
    prev = round(pts[-2][1], 2) if len(pts) > 1 else None
    return {"close": round(c, 2), "prev_close": prev, "date": datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")}

def _stooq(t):
    url = "https://stooq.com/q/l/?s=%s.us&f=sd2t2ohlcv&h&e=csv" % t.lower()
    with urllib.request.urlopen(url, timeout=10) as r:
        row = next(csv.DictReader(io.StringIO(r.read().decode())))
    if row.get("Close") in (None, "", "N/D"):
        raise ValueError("no data (bad ticker or empty data)")
    return {"close": round(float(row["Close"]), 2), "date": row["Date"]}

def get_prices(tickers, allow_sample=False):
    """Return {ticker: {"close", "date", "source"} or {"error": "..."}}. Never raises."""
    out = {}
    for t in tickers:
        t = t.strip().upper()
        errors = []
        for name, fn in (("yahoo (yfinance)", _yahoo), ("yahoo chart (stdlib fallback)", _yahoo_chart), ("stooq (fallback)", _stooq)):
            try:
                out[t] = dict(fn(t), source=name); break
            except ImportError:
                errors.append(name + ": yfinance not installed")
            except Exception as e:
                errors.append("%s: %s" % (name, e))
        else:
            if allow_sample and t in SAMPLE_PRICES:
                out[t] = dict(SAMPLE_PRICES[t], source="SAMPLE DATA (not real)")
            else:
                out[t] = {"error": "Could not get a price for %s. %s" % (t, "; ".join(errors))}
    return out

if __name__ == "__main__":
    for t, v in get_prices(["NVDA", "MSFT", "VOO", "ZZZZ"]).items():
        print(t, v)

import os
PROJECT = os.path.dirname(os.path.abspath(__file__))

def write_report(text, filename="report.md"):
    """Save the report inside the project folder only. Returns (ok, message). Never raises."""
    path = os.path.realpath(os.path.join(PROJECT, filename))
    if os.path.commonpath([path, os.path.realpath(PROJECT)]) != os.path.realpath(PROJECT):
        return False, "REFUSED: %s is outside the project folder" % filename
    try:
        with open(path, "w") as f:
            f.write(text)
        return True, "saved " + os.path.relpath(path, PROJECT)
    except Exception as e:
        return False, "could not save: %s" % e

def build_report(prices):
    """Make the report text with the 4 required sections."""
    live = [t for t, v in prices.items() if "close" in v and "SAMPLE" not in v["source"]]
    sample = any("SAMPLE" in v.get("source", "") for v in prices.values())
    L = ["# Daily stock recap", "", "## Summary",
         "Recap for %s. %s" % (", ".join(prices), "SAMPLE DATA - prices are NOT real." if sample else "%d of %d prices are live." % (len(live), len(prices))),
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
