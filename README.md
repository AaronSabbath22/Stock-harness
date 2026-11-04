# stock-harness

**A small, safe AI-agent harness in plain Python that writes a daily stock recap.**
Built by Aaron as a 10-session learning project (one hour a night, two weeks).

> **Learning only. No trading.** This project only *reads* free price data and *writes* a report.
> It cannot buy, sell, or connect to a brokerage. Nothing here is financial advice.

## What it does
`python run.py` runs one complete agent loop:
1. Reads the job card (`task.json`).
2. Fetches the latest closing prices for NVDA, MSFT and VOO (up to 3 tries).
3. Writes `report.md` with Summary, Prices, Notes and Disclaimer sections.
4. Runs three checks: freshness, price sanity and required sections.
5. Asks a human before any action (the only action is a **fake** email that just prints).
6. Saves `receipt.json`, a record of everything that happened.

## The 7 harness parts
| # | Harness part | Where it lives | What it does |
|---|---|---|---|
| 1 | Task contract | `task.json` | goal, output, constraints, done_when |
| 2 | Map for humans and AIs | `AGENTS.md` | file map, rules, permission table, how to run |
| 3 | Tools + permissions | `tools.py`, `AGENTS.md` | `get_prices` (read-only, clear errors), `write_report` (refuses paths outside the project) |
| 4 | Memory | `state.py`, `state.json` | decisions, failures, pending items; survives restarts |
| 5 | Checks | `checks.py` | data within 4 days; price > 0 and moved 50% or less; all report sections present |
| 6 | Approval gate | `approval.py` | only a typed `yes` allows an action; no input means NO |
| 7 | Trace, retries, escalation | `trace.py` | one JSON line per step in `trace.jsonl`; 3-try cap; then NEEDS HUMAN |

The run itself is `run.py`. Every part has its own test: `check_*.py`.

## Run it on a computer
Requires Python 3.9 or newer. No installs needed: it uses only the standard library.
```
python run.py              # full loop, prints the receipt
python run_on_phone.py     # runs all 9 session checks, PASS/FAIL summary
```
Optional: `pip install yfinance` to use it as the first price source. Without it, the tool uses
Yahoo's public chart endpoint, then Stooq. Free data can be late or missing.

## Run it on a phone
`phone_single_file.py` is one self-contained file (standard library only). Copy all of it into an
iPhone Python app (tested in Python Code Pad), delete anything already there, and tap Run.
Offline, it falls back to clearly labeled **SAMPLE DATA** and the freshness check fails on purpose.
See `PHONE_SETUP.md`.

## Sample receipt (phone, live data, Nov 3, 2026)
```
=========== RUN RECEIPT ===========
Task:        Write a daily recap for NVDA, MSFT, VOO
Data:        live (1 fetch try)
  NVDA  $206.69 on 2026-11-03
  MSFT  $520.99 on 2026-11-03
  VOO   $693.54 on 2026-11-03
Check freshness: PASS
Check sanity:    PASS
Check sections:  PASS
Approval:    send report by email (FAKE) -> approved
Status:      DONE
Learning only. Never trades. Not financial advice.
===================================
```

## Sample report.md
```
# Daily stock recap

## Summary
Recap for NVDA, MSFT, VOO. 3 of 3 prices are live.

## Prices
- NVDA: $206.69 on 2026-11-03 (+2.29% vs prev close)
- MSFT: $520.99 on 2026-11-03 (+2.74% vs prev close)
- VOO: $693.54 on 2026-11-03 (+0.32% vs prev close)

## Notes
Free data can be late or missing. Checks run before this report is trusted.

## Disclaimer
Learning project only. Not financial advice. This tool never trades.
```

## Safety notes
- Read-only by design: there is no trading code and no brokerage connection.
- The "send email" action is fake. It only prints, and it still needs a typed `yes`.
- No passwords, API keys or accounts are used or stored.
- The report writer refuses to save outside the project folder.
- Retries are capped at 3, then the agent stops and asks a human.

## What I learned
How to give an AI agent a clear job, safe tools, memory, checks, a human approval step and
a trace log, so its work can be trusted and audited.

Author: Aaron. License: free to read and learn from.
