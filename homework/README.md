# Week 2 homework: build an MCP server Copilot can call

About an hour, at your own pace. Everything is in `mcp_homework.ipynb`.

## You need

- VS Code with GitHub Copilot (Chat, in Agent mode) and the Jupyter extension
- Python 3.10 or newer, with `pip install "mcp>=2.2" ipykernel`. In a virtual environment, also register it
  as a kernel so VS Code lists it by name: `python -m ipykernel install --user --name ai-sdlc-week2-mcp --display-name "AI-SDLC week 2 (mcp 2.2)"`

## Start

1. Open this folder in VS Code and open `mcp_homework.ipynb`.
2. Pick your Python as the kernel (top right of the notebook).
3. Run Part 0. It should say **READY**.

## What's here

| File | What it is |
| --- | --- |
| `mcp_homework.ipynb` | The homework, in six parts, with answers at the bottom |
| `data/claims.json`, `data/policies.json` | Fake UK home and motor claims and policies |
| `data/claims.original.json` | A clean copy; the notebook's reset cell restores from it |
| `planted-note.txt` | The customer's note for Part 5 |
| `wiretap.py` | Logs every message between Copilot and your server to `wire.log` |

The notebook creates `server.py` here when you run Part 1. All the data is made up.
