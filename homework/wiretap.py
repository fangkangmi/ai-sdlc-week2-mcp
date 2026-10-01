"""Sit between an MCP client and a stdio server, and log every JSON line in both directions.

Usage: python wiretap.py <log file> <server command...>
Point the client (VS Code, Copilot CLI, Codex) at this script instead of the server, for example
"command": "<python>", "args": ["<path>/wiretap.py", "<path>/wire.log", "<python>", "<path>/server.py"].
Lines are logged as "-> " (client to server) and "<- " (server to client).
"""
import subprocess
import sys
import threading

log_path, command = sys.argv[1], sys.argv[2:]
log = open(log_path, "a", buffering=1)
server = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)


def to_server():
    for line in sys.stdin:
        log.write("-> " + line)
        server.stdin.write(line)
        server.stdin.flush()
    server.stdin.close()


threading.Thread(target=to_server, daemon=True).start()
for line in server.stdout:
    log.write("<- " + line)
    sys.stdout.write(line)
    sys.stdout.flush()
sys.exit(server.wait())
