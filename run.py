"""run.py - Session 9: the whole loop in one command. Learning only, never trades."""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tools, checks, state, approval
import trace as tr

def main(ask=input):
    start = datetime.datetime.now()
    tries = {"n": 0}
    with open(os.path.join(HERE, "task.json")) as f:
        task = json.load(f)
    tickers = ["NVDA", "MSFT", "VOO"]
    tr.log("start", "task: " + task["goal"])

    def fetch(t):
        tries["n"] += 1
        return tools.get_prices(t)
    prices = tr.fetch_with_retry(fetch, tickers, wait=2)
    receipt = {"start": start.isoformat(timespec="seconds"), "task": task["goal"], "tickers": tickers,
               "fetch_tries": tries["n"], "retries_used": max(0, tries["n"] - 1)}
    if prices is None:
        receipt.update(status="NEEDS HUMAN", checks={}, approvals=[])
    else:
        sources = sorted({v.get("source", "error") for v in prices.values()})
        text = tools.build_report(prices)
        saved_ok, saved_msg = tools.write_report(text, task["output"])
        tr.log("write_report", saved_msg)
        results = checks.run_all(prices, text)
        for name, (ok, msg) in results.items():
            tr.log("check " + name, ("pass: " if ok else "FAIL: ") + msg)
        all_ok = saved_ok and all(ok for ok, _ in results.values())
        approvals = []
        if all_ok:
            sent = approval.send_report_by_email(text, ask)
            approvals.append({"action": "send report by email (FAKE)", "approved": sent is not None})
            tr.log("approval", "approved" if sent else "blocked")
        else:
            state.add_pending("Checks failed; report not trusted. Review report.md.")
        receipt.update(status="DONE" if all_ok else "CHECKS FAILED", sources=sources,
                       report=task["output"] if saved_ok else None,
                       checks={k: {"passed": ok, "detail": m} for k, (ok, m) in results.items()},
                       approvals=approvals)
    receipt["end"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(os.path.join(HERE, "receipt.json"), "w") as f:
        json.dump(receipt, f, indent=2)
    tr.log("finish", receipt["status"])
    print(json.dumps(receipt, indent=2))
    return receipt

if __name__ == "__main__":
    main()
