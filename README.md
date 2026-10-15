# StudyBuddy Assessment 4

Krishi Patel · 12254297 · COIT12204

This extends the supplied Assessment 3 StudyBuddy: its sample tasks and three
local tools are preserved in `app/tools.py`. Planner and Worker replace the
single-agent wrapper. The default is an explicitly labelled rule-based demo;
optional Gemini mode adds model-based planning. No API key is included.

## Start on Windows in VS Code

1. Extract the ZIP completely (do not run inside the compressed folder).
2. Open the extracted `StudyBuddy_A4` folder containing `run.py` in VS Code.
3. Open Terminal → New Terminal. Python 3.11 or newer is recommended; tested on 3.12.
4. Run these commands in PowerShell, one line at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-tested.txt
.\.venv\Scripts\python.exe run.py
```

This uses the virtual environment directly, so PowerShell activation policy is
not an obstacle. If `py` is unavailable but Python is installed, use `python`
for the first command. Keep the terminal running.

Normal website: http://127.0.0.1:8000/
API documentation: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health

Stop with Ctrl+C. If port 8000 is busy:

```powershell
.\.venv\Scripts\python.exe run.py --port 8001
```

Open http://127.0.0.1:8001/ and http://127.0.0.1:8001/docs in that case.
For macOS/Linux: `python3 -m venv .venv`, then use `.venv/bin/python` in
place of `.\.venv\Scripts\python.exe` for the remaining commands.
`requirements-tested.txt` pins the directly tested packages; `requirements.txt`
is a compatible-range alternative. Transitive dependencies are not fully locked.
First-time installation needs internet. Swagger's default assets also need
internet; the normal website uses only bundled local assets.

## Run tests and regenerate evidence

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe evaluate.py
```

The supplied test record reports 25 passed with one upstream Starlette
TestClient deprecation warning. This is not a failed application test.
`evaluate.py` generates three successful interactions and four deliberate
failure runs in `evidence/`. Runtime traces append to `logs/messages.jsonl`.
Included log-extract figures reproduce actual executions in the development
environment; they are not screenshots. Browser capture was unavailable here.
Repeat the demonstrations and capture your own screenshots before submission.

## Demonstrate in the normal website

Use the three example buttons, then select Worker timeout and run again.
The answer panel, message trace and JSON download show the outcome.
Other deliberate failures: invalid output, unknown receiver and iteration limit.
These controls are for a local educational demonstration, not production use.

## Demonstrate in Swagger

Expand POST `/api/agent`, click Try it out, enter a request and Execute:

```json
{"message":"Summarise all tasks","mode":"local","scenario":"normal","max_steps":4,"timeout_seconds":10}
```

Then use `When is task 1 due?` and
`Classify report due in 2 days, blocking other work`.
To show timeout, use `scenario: "timeout"` and `timeout_seconds: 0.1`.
A controlled fallback is HTTP 200 with `status: "fallback"`; malformed HTTP
inputs return 422. Check the status field, not just the HTTP status code.
GET `/api/agent/state` exposes run counters and the latest 100 run summaries.

## Optional live Gemini planning

Copy `.env.example` to `.env`. Set your own `GEMINI_API_KEY` and `GEMINI_MODEL`
to a model available to your account, restart, then select Gemini in the website.
Never commit `.env` or paste the key into screenshots. Live mode sends the request
to Google, so use fictional study tasks only. It uses the Gemini REST API with
JSON output, followed by local Pydantic validation. The Worker stays deterministic.
A live API request was not tested for this delivery: no user credential was used.
Missing configuration, timeout, quota or malformed output produces a labelled
fallback; it never silently reports local output as Gemini success. The original
LangChain dependency is replaced by a smaller HTTP adapter. This is documented
as a deliberate architecture change, not an unchanged LangChain implementation.

## Code map

- `app/models.py`: strict request, plan, message, result and response contracts.
- `app/agents.py`: separate Planner and Worker implementations, optional model adapter.
- `app/orchestrator.py`: validated routing, bounded steps, timeouts, state and JSONL logging.
- `app/tools.py`: original A3 read-only task tools and historical sample dates.
- `app/main.py`: FastAPI routes and static website.
- `app/static/`: bundled HTML, CSS and JavaScript.
- `tests/test_system.py`: behavioural, failure, concurrency and API regression tests.
- `evaluate.py`: repeatable evaluation and real run evidence.

A normal pipeline has three routed messages: orchestrator → planner,
planner → worker, worker → orchestrator. SENT and RECEIVED share the same message
and run ID. Invalid receivers are logged as attempted sends but never delivered.
The step cap counts successful deliveries, not log entries. Every attempt to
exceed the cap terminates; there are no hidden retries.

## Known limits

Read-only, single-process, unauthenticated local prototype; no task editing,
shared database, deployment hardening or long-term state. Counters reset on
restart; JSONL logs remain on disk and need manual retention management. Local
parsing supports the documented English examples, not arbitrary natural language
or every form of negation. Schema validation cannot prove model interpretations
are correct. Async deadlines cannot interrupt a blocking CPU-bound function;
the supplied tools are small and synchronous. Do not expose the demo publicly.

## Assessment checklist

- Review the supplied report and its AI declaration; do not claim independent
  authorship or claim a live model run without evidence.
- Brief conflict: opening length is 1,800–2,000; technical report is 1,000–1,500.
  The report separates main narrative and an additional appendix; confirm your
  tutor's intended counting rule.
- Create a GitHub/GitLab repository, upload the source files (exclude `.env`,
  `.venv`, caches and private logs), and include the repository URL in Moodle.
- Record your own 3–5 minute video. See DEMONSTRATION.md.
- Submit the Word report and code/repository as instructed. A ZIP does not
  replace the expressly required repository or your demonstration video.

## AI assistance declaration

ChatGPT assisted with analysis of the supplied brief, code extension, automated
tests, documentation and report drafting. The package records development-
environment checks. The student must review, understand and independently verify
the work, and add their own evidence/reflection before submission.
