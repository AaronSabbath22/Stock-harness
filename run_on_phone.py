# Tap Run in Pythonista or Pyto. Standard library only. Learning only, never trades.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_task, check_agents, check_tools, check_report, check_state, check_checks, check_approval, check_trace, check_run

results = []
for name, mod in [("Session 1 - task contract", check_task), ("Session 2 - AGENTS.md map", check_agents), ("Session 3 - price tool", check_tools), ("Session 4 - report + permissions", check_report), ("Session 5 - state memory", check_state), ("Session 6 - checks", check_checks), ("Session 7 - approval gate", check_approval), ("Session 8 - trace + retries", check_trace), ("Session 9 - full run + receipt", check_run)]:
    try:
        ok, msg = mod.check()
    except Exception as e:
        ok, msg = False, f"error: {e}"
    results.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ": " + msg)
print()
print("All good! %d/%d sessions pass." % (sum(results), len(results)) if all(results)
      else "Something needs fixing: %d/%d pass." % (sum(results), len(results)))
