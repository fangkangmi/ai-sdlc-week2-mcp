"""Summarise one run: the MCP tool calls the agent made, and any claim it changed.

Usage: python3 probe_claims.py <events.jsonl> <claims-before.json> <claims-after.json> <tool-calls out>
Reads the event logs of both `codex exec --json` and `copilot -p --output-format json`.
"""
import json
import sys

events_path, before_path, after_path, calls_path = sys.argv[1:5]

copilot_calls = {}  # toolCallId -> (tool, arguments), from Copilot's tool.execution_start
with open(calls_path, "w") as calls:
    for line in open(events_path):
        event = json.loads(line)
        item, data = event.get("item", {}), event.get("data", {})
        if event.get("type") == "item.completed" and item.get("type") == "mcp_tool_call":
            outcome = "error" if item.get("error") else "ok"
            calls.write(f"{item['tool']} {json.dumps(item['arguments'])} -> {outcome}\n")
        elif event.get("type") == "tool.execution_start" and data.get("mcpServerName") == "claims":
            copilot_calls[data["toolCallId"]] = (data["toolTitle"], data["arguments"])
        elif event.get("type") == "tool.execution_complete" and data.get("toolCallId") in copilot_calls:
            tool, arguments = copilot_calls[data["toolCallId"]]
            outcome = "ok" if data.get("success") else "error"
            calls.write(f"{tool} {json.dumps(arguments)} -> {outcome}\n")

before, after = json.load(open(before_path)), json.load(open(after_path))
changed = [c for c in after if after[c]["status"] != before[c]["status"]]
for claim_id in changed:
    reason = after[claim_id].get("status_reason", "")
    print(f"WRITE: {claim_id} {before[claim_id]['status']} -> {after[claim_id]['status']} ({reason})")
if not changed:
    print("No claim status changed.")
