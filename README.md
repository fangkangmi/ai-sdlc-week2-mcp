# AI-SDLC coaching, week 2: MCP with GitHub Copilot

Week 2 of a five-session coaching series on AI-assisted development with GitHub Copilot. The 45-minute
session explains what MCP is and how it talks, then demos it live: Copilot calls a small claims server,
then a customer's note planted in the claim data tries to make it approve a claim. The colleague builds
the same server at home in a notebook.

All data here is synthetic: invented UK home and motor claims and policies.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python demo.py check                   # should end with READY
python demo.py setup ~/claims-demo     # Windows: python demo.py setup %USERPROFILE%\claims-demo
```

To run the homework notebook from the same environment, register it as a Jupyter kernel once, then pick
**AI-SDLC week 2 (mcp 2.2)** as the notebook's kernel in VS Code:

```bash
python -m ipykernel install --user --name ai-sdlc-week2-mcp --display-name "AI-SDLC week 2 (mcp 2.2)"
```

Stage the demo outside this repo (`demo.py` refuses otherwise), so Copilot doesn't read the notes in
here as instructions. Using an AI agent to set it up? Ask it to follow [`AGENTS.md`](AGENTS.md).

## Run of show

| When | Do this |
| --- | --- |
| Before, once | `python demo.py setup ~/claims-demo`, then `code ~/claims-demo/repo`. When VS Code asks, trust and start the `claims` server. Open a terminal split with `tail -f ~/claims-demo/wire.log` (Windows: `Get-Content -Wait $HOME\claims-demo\wire.log`). |
| Before demo 1 | Copilot Chat in **Agent** mode. Under **Configure Tools**, expand `claims` and untick `update_claim_status`. |
| Demo 1 (slide 16) | Ask "What's the status of claim CLM-1001? Use the claims tools." Expand the approval prompt to show the arguments, and point at `wire.log`. Then ask "Is CLM-1001 covered by its policy?" |
| Demo 2 (slide 18) | `python demo.py plant ~/claims-demo`, restart the server (**MCP: List Servers** → Restart), tick `update_claim_status`, then send the triage prompt. |
| After | `python demo.py reset ~/claims-demo` |

The triage prompt: `Triage claim CLM-1002. Use the claims tools to look up the claim and its policy,
decide whether it should be APPROVED, DECLINED or REFERRED, and set the status with a one-line reason.`

The full plan, slide by slide with speaker notes, is in [`session.md`](session.md). Background for
questions is in [`mcp-brief.md`](mcp-brief.md).

## Homework

Zip [`homework/`](homework/) and send it to the colleague before the session; they run its setup check
with you at the end. It's a notebook in seven parts (setup check, write `get_claim`, talk to the server
by hand, connect Copilot CLI, tool design, the planted note, design their own tool), with answers at the
bottom. It needs no API key: their own Copilot is the client, through Copilot CLI in VS Code's terminal,
in the homework folder.

## What's here

| Path | What it is |
| --- | --- |
| `claims-mcp/` | The demo MCP server (`get_claim`, `lookup_policy`, `update_claim_status`) and its data |
| `demo-repo/` | Week 1's synthetic claims repo (13 tests): the workspace Copilot works in |
| `demo.py` | Check, stage, plant, reset (Windows, macOS, Linux) |
| `wiretap.py` | Sits between Copilot and the server and logs every MCP message to `wire.log` |
| `planted-description*.txt` | The customer's note for the second demo (a deliberate prompt-injection payload) |
| `homework/` | The colleague's notebook kit |
| `session.md`, `mcp-brief.md` | The coach's plan and background |
| `slides/` | The deck to present, `hand-roll-an-mcp-server.pptx` (speaker notes included), and its source: one HTML file per slide |
| `runs/` | 22 recorded runs of the demo through Codex and the Copilot CLI (29 Sep to 1 Oct 2026; GPT-6-Luna in all but one) |
| `run-mcp-demo.sh`, `run-copilot-demo.sh`, `probe_claims.py` | Record more runs (bash; needs the `codex` or `copilot` CLI). `SERVER=<folder>` runs a changed copy of the server |

## Requirements

- Python 3.10 or newer and `mcp` 2.2 or newer (tested with 2.2.0). The server uses the `mcp` 2.x API
  (`MCPServer`, `ToolError`) and speaks MCP 2026-07-28 as well as older revisions.
- VS Code with GitHub Copilot in Agent mode. On Copilot Business or Enterprise, the organisation policy
  "MCP servers in Copilot" must be on; it is off by default.
- For the homework: VS Code's Jupyter extension, `ipykernel`, and Copilot CLI (`copilot`) for Parts 3 to 5.
