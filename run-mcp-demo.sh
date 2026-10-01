#!/usr/bin/env bash
# Run one prompt headlessly through Codex with the claims MCP server attached.
# Run it from anywhere: ./run-mcp-demo.sh [--plant] <run name> "<prompt>" [model]
# --plant puts planted-description.txt into CLM-1002's description (the customer's own text).
# PLANT_FILE=<file> plants a different text instead.
# Output: runs/<run name>/{last-message.txt,events.jsonl,tool-calls.txt,probe.txt}
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
plant=0
if [[ "${1:-}" == --plant ]]; then plant=1; shift; fi
name="$1"; prompt="$2"; model="${3:-gpt-6-luna}"
# Any Python with the mcp package: this repo's .venv if there is one. Not realpath: that follows the
# venv symlink to the system Python.
python="${PYTHON:-$here/.venv/bin/python}"
[[ -x "$python" ]] || python=python3
"$python" -c "import mcp" || { echo "No mcp package in $python; set PYTHON=" >&2; exit 1; }
out="$here/runs/$name"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# The server sits outside the workspace, like a real claims system: the agent sees its data only
# through the tools. The workspace is a fresh copy of week 1's repo.
cp -r "$here/claims-mcp" "$work/server"
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

mkdir -p "$out"
# --ignore-user-config + --disable memories: the model sees the repo, the prompt and the tools.
# approval_mode="approve" runs every claims tool without asking: the "Allow all" setting in VS Code.
codex exec -m "$model" --ignore-user-config --disable memories --ephemeral \
  -s workspace-write -C "$work/repo" --json -o "$out/last-message.txt" \
  -c "mcp_servers.claims.command=\"$python\"" \
  -c "mcp_servers.claims.args=[\"$work/server/server.py\"]" \
  -c 'mcp_servers.claims.default_tools_approval_mode="approve"' \
  "$prompt" < /dev/null | sed "s#$work#<tmp>#g" > "$out/events.jsonl"

"$python" "$here/probe_claims.py" "$out/events.jsonl" "$work/claims-before.json" \
  "$work/server/data/claims.json" "$out/tool-calls.txt" > "$out/probe.txt"

echo "== $out"
cat "$out/last-message.txt"
echo; cat "$out/tool-calls.txt" "$out/probe.txt"
