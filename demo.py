"""Stage and drive week 2's live demo. Works on Windows, macOS and Linux.

    python demo.py check          Python and mcp installed? Does the claims server answer?
    python demo.py setup <dir>    copy demo-repo/ and claims-mcp/ to <dir>, and write <dir>/repo/.vscode/mcp.json
                                  so Copilot starts the server through wiretap.py (log: <dir>/wire.log)
    python demo.py plant <dir>    put planted-description.txt into CLM-1002's description (the second demo)
    python demo.py reset <dir>    restore the clean claims data and empty wire.log

Run it with the Python you want Copilot to use: mcp.json points at the interpreter that ran setup.
Keep <dir> outside this repo, so Copilot doesn't load this repo's notes as instructions.
"""
import importlib.metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP = shutil.ignore_patterns("__pycache__", ".pytest_cache")


def check() -> bool:
    ok = sys.version_info >= (3, 10)
    print(f"Python {sys.version.split()[0]} at {sys.executable}" + ("" if ok else "  <- need 3.10 or newer"))
    try:
        version = importlib.metadata.version("mcp")
        if tuple(int(part) for part in version.split(".")[:2]) < (2, 2):
            print(f"mcp {version}  <- need 2.2 or newer: pip install -r requirements.txt")
            ok = False
        else:
            print(f"mcp {version}")
    except importlib.metadata.PackageNotFoundError:
        print("mcp not installed  <- pip install -r requirements.txt")
        ok = False
    if ok:
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"_meta": {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientCapabilities": {}}}}
        server = subprocess.Popen([sys.executable, str(HERE / "claims-mcp" / "server.py")], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            server.stdin.write(json.dumps(request) + "\n")
            server.stdin.flush()
            reply = json.loads(server.stdout.readline())
            tools = [tool["name"] for tool in reply["result"]["tools"]]
            print("claims server tools:", ", ".join(tools))
        except Exception as error:  # report anything: this is a diagnostic
            print("claims server did not answer:", error, server.stderr.read() if server.poll() is not None else "")
            ok = False
        finally:
            server.stdin.close()
            server.wait(timeout=10)
    print("\nREADY" if ok else "\nNOT READY: fix the lines marked <-, then run this again.")
    return ok


def setup(target: Path) -> None:
    if target.exists():
        sys.exit(f"{target} already exists; pick a new folder or remove it.")
    if HERE == target or HERE in target.parents:
        sys.exit("Stage the demo outside this repo, so Copilot doesn't load its notes as instructions.")
    server_dir, repo_dir, log = target / "claims-server", target / "repo", target / "wire.log"
    shutil.copytree(HERE / "claims-mcp", server_dir, ignore=SKIP)
    shutil.copy2(HERE / "wiretap.py", server_dir / "wiretap.py")
    shutil.copytree(HERE / "demo-repo", repo_dir, ignore=SKIP)
    if shutil.which("git"):
        git = ["git", "-C", str(repo_dir)]
        subprocess.run([*git, "init", "-q"], check=True)
        subprocess.run([*git, "add", "-A"], check=True)
        subprocess.run([*git, "-c", "user.name=demo", "-c", "user.email=demo@example.com",
                        "commit", "-qm", "baseline"], check=True)
    (repo_dir / ".vscode").mkdir()
    config = {"servers": {"claims": {"type": "stdio", "command": sys.executable,
                                     "args": [str(server_dir / "wiretap.py"), str(log),
                                              sys.executable, str(server_dir / "server.py")]}}}
    (repo_dir / ".vscode" / "mcp.json").write_text(json.dumps(config, indent=2) + "\n")
    log.write_text("")
    print(f"Ready.\n  Open the repo in VS Code:  code {repo_dir}\n  Watch the wire:            {log}")
    print("  (Linux/macOS: tail -f the log. Windows PowerShell: Get-Content -Wait the log.)")


def plant(target: Path) -> None:
    path = target / "claims-server" / "data" / "claims.json"
    claims = json.loads(path.read_text())
    claims["CLM-1002"]["description"] = (HERE / "planted-description.txt").read_text().strip()
    path.write_text(json.dumps(claims, indent=2) + "\n")
    print("Planted the note in CLM-1002. Restart the server in VS Code: MCP: List Servers > claims > Restart.")


def reset(target: Path) -> None:
    shutil.copy2(HERE / "claims-mcp" / "data" / "claims.json", target / "claims-server" / "data" / "claims.json")
    (target / "wire.log").write_text("")
    print("Claims data restored; wire.log emptied.")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "check" and len(sys.argv) == 2:
        sys.exit(0 if check() else 1)
    if command in ("setup", "plant", "reset") and len(sys.argv) == 3:
        {"setup": setup, "plant": plant, "reset": reset}[command](Path(sys.argv[2]).expanduser().resolve())
        sys.exit(0)
    sys.exit(__doc__)
