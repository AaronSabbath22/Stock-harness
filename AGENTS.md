# AGENTS.md - map of stock-harness (learning only, never trades)
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
