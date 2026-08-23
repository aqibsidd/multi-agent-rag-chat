# ERRORS

Failure log, append-only. When the same preventive rule would have caught a
second failure, promote it into root `AGENTS.md` under "Learned rules".

## ERR-001

Task: TASK-008

Classification: DEPENDENCY

Symptom: `from langchain_text_splitters import RecursiveCharacterTextSplitter`
failed with `ModuleNotFoundError` — not installed, and not pulled in
transitively by `langchain` in this version.

Root cause: TASK-001's `requirements.txt` omitted
`langchain-text-splitters`, since the recursive char splitter used to ship
inside the core `langchain` package in older versions.

Fix: added `langchain-text-splitters` to `backend/requirements.txt`,
installed it. No application code touched to work around this (per
failure-taxonomy.md's DEPENDENCY rule).

Preventive rule: when adding a new import from a LangChain sub-package,
confirm it's actually installed before writing code against it, not after
a test fails.

Status: RESOLVED
