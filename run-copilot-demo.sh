#!/usr/bin/env bash
# Run one prompt headlessly through the GitHub Copilot CLI with the claims MCP server attached.
# Run it from anywhere: ./run-copilot-demo.sh [--plant] <run name> "<prompt>" [model]
# Same setup as run-mcp-demo.sh; wiretap.py also records every MCP message between Copilot and the server.
# Each run uses one premium request from your Copilot plan.
# Output: runs/<run name>/{last-message.txt,events.jsonl,wire.log,tool-calls.txt,probe.txt}
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
plant=0
if [[ "${1:-}" == --plant ]]; then plant=1; shift; fi
name="$1"; prompt="$2"; model="${3:-auto}"
# Any Python with the mcp package: this repo's .venv if there is one. Not realpath: that follows the
# venv symlink to the system Python.
python="${PYTHON:-$here/.venv/bin/python}"
[[ -x "$python" ]] || python=python3
"$python" -c "import mcp" || { echo "No mcp package in $python; set PYTHON=" >&2; exit 1; }
out="$here/runs/$name"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cp -r "${SERVER:-$here/claims-mcp}" "$work/server"  # SERVER=<dir> runs a variant of the server
cp -r "$here/demo-repo" "$work/repo"
find "$work" -name __pycache__ -type d -prune -exec rm -rf {} +
git -C "$work/repo" init -q
git -C "$work/repo" add -A
git -C "$work/repo" -c user.name=demo -c user.email=demo@example.com commit -qm baseline

if (( plant )); then
  "$python" - "$work/server/data/claims.json" "${PLANT_FILE:-$here/planted-description.txt}" <<'EOF'
import json, sys
path, planted = sys.argv[1], open(sys.argv[2]).read().strip()
claims = json.load(open(path))
claims["CLM-1002"]["description"] = planted
open(path, "w").write(json.dumps(claims, indent=2) + "\n")
EOF
fi
cp "$work/server/data/claims.json" "$work/claims-before.json"

cat > "$work/mcp.json" <<EOF
{"mcpServers": {"claims": {"type": "stdio", "command": "$python",
  "args": ["$here/wiretap.py", "$work/wire.log", "$python", "$work/server/server.py"], "tools": ["*"]}}}
EOF

mkdir -p "$out"
# --disable-builtin-mcps: only the claims tools, no GitHub MCP server. --allow-all-tools: every tool runs
# without asking, the "Allow all" setting in VS Code; file access stays limited to the workspace.
copilot -C "$work/repo" -p "$prompt" --model "$model" --additional-mcp-config "@$work/mcp.json" \
  --disable-builtin-mcps --allow-all-tools --output-format json --log-dir "$work/logs" \
  < /dev/null | sed "s#$work#<tmp>#g" > "$out/events.jsonl"
sed "s#$work#<tmp>#g; s#$here#<week-02>#g" "$work/wire.log" > "$out/wire.log"

"$python" - "$out/events.jsonl" "$out/last-message.txt" <<'EOF'
import json, sys
last = ""
for line in open(sys.argv[1]):
    event = json.loads(line)
    if event.get("type") == "assistant.message" and event["data"].get("content"):
        last = event["data"]["content"]
open(sys.argv[2], "w").write(last + "\n")
EOF
"$python" "$here/probe_claims.py" "$out/events.jsonl" "$work/claims-before.json" \
  "$work/server/data/claims.json" "$out/tool-calls.txt" > "$out/probe.txt"

echo "== $out"
cat "$out/last-message.txt" "$out/tool-calls.txt" "$out/probe.txt"
