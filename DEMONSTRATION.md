# A simple four minute demonstration

0:00–0:35 — Open the normal website. Introduce yourself and explain that this
extends your Assessment 3 StudyBuddy. The Planner interprets a request; the Worker
uses the original task tools. State honestly whether local or Gemini mode is used.

0:35–1:20 — Run Summarise all tasks. Show the answer and scroll to Message trace.
Explain sender, receiver, intent, content, run ID and step. Show the Planner →
Worker execute message and Worker → Orchestrator result. Point to matching SENT
and RECEIVED records.

1:20–2:00 — Run task 1 lookup, then the priority example. Explain that the Worker
retrieves stored facts and uses deterministic urgency rules. Historical dates
are the original A3 fixtures, not current deadlines.

2:00–2:50 — Select Worker timeout. Run it. Show ERROR, FALLBACK and RUN_END.
Explain that wait_for cancels the waiting operation, no task was changed, and
the application remains available. Select Normal run and run again to prove
recovery. You can also show Unknown receiver or Iteration limit.

2:50–3:25 — Open /docs and GET /api/agent/state. Show run_count and error_count.
In VS Code, show app/models.py and the routing whitelist in app/orchestrator.py.
Explain that an invalid destination is never delivered.

3:25–4:00 — Show your own pytest result and logs/messages.jsonl. Mention the
missing-deadline and not-blocking fixes. Explain limitations: local rules are
not live AI, state resets on restart, and live Gemini needs valid configuration.
Acknowledge AI assistance accurately. Stop recording within five minutes.
