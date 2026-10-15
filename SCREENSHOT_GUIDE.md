# Required screenshots to add to the report

The supplied report uses authentic execution-log extracts, not browser screenshots.
The brief explicitly requests screenshots. Capture these on your own computer:

1. Run the website, choose Task overview, click Run the agents, and capture the
   answer together with the Message trace showing SENT and RECEIVED.
2. Choose Look up task 1, run, and capture the answer and routed content.
3. Choose Check priority, run, and capture the deadline, blocking flag and result.
4. Select Worker timeout, run, and capture ERROR, FALLBACK and RUN_END.
5. Select Invalid worker output, run, and capture its validation failure trace.
6. In the VS Code terminal run the pytest command in README. Capture the result.

On Windows use Win+Shift+S. Save each image, insert it beside the matching figure
in Word, and keep the caption. Show the run ID so the screenshot can be linked
to the downloaded JSON. You may need two captures for a long trace. Do not include
API keys or unrelated personal information. Do not change recorded outputs.

Also record the required 3–5 minute video and upload your code to GitHub/GitLab.
