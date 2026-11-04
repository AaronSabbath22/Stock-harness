"""approval.py - Session 7: nothing risky happens without a typed 'yes'. Learning only."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state

def approve(action, ask=input, state_path=state.STATE_FILE):
    """Return (approved, message). Only an exact typed 'yes' approves."""
    print("APPROVAL NEEDED: " + action)
    try:
        answer = ask("Type yes to allow, anything else to block: ")
    except (EOFError, OSError, RuntimeError) as e:
        msg = "no input available (%s) - treated as NO (safe default)" % type(e).__name__
        state.add_failure("BLOCKED '%s': %s" % (action, msg), state_path)
        return False, msg
    if answer.strip().lower() == "yes":
        state.add_decision("APPROVED '%s'" % action, state_path)
        return True, "approved by human"
    state.add_failure("BLOCKED '%s': human answered %r" % (action, answer), state_path)
    return False, "blocked: answer was %r" % answer

def fake_send_email(report_text):
    """FAKE action. Never sends anything; only prints."""
    print("[FAKE] Would email report (%d chars). Nothing was sent." % len(report_text))
    return "fake-sent"

def send_report_by_email(report_text, ask=input, state_path=state.STATE_FILE):
    ok, msg = approve("send report by email", ask, state_path)
    if not ok:
        print("STOPPED: " + msg)
        return None
    return fake_send_email(report_text)
