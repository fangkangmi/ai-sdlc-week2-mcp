"""A tiny MCP server over fake claims data. Week 2's hand-roll target."""
import json
import re
from pathlib import Path
from typing import Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

DATA = Path(__file__).parent / "data"
POLICY_NUMBER = re.compile(r"[A-Z]{3}\d{7}")

mcp = MCPServer("claims")


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text())


@mcp.tool()
def get_claim(claim_id: str) -> dict:
    """Get one insurance claim by ID, for example CLM-1001: its policy number, incident date,
    amount in GBP, the customer's own description, and current status."""
    claims = load("claims.json")
    if claim_id not in claims:
        raise ToolError(f"No claim {claim_id}. Claim IDs look like CLM-1001; check the ID on the ticket.")
    return {"claim_id": claim_id, **claims[claim_id]}


@mcp.tool()
def lookup_policy(policy_number: str) -> dict:
    """Look up a UK home or motor insurance policy by policy number (three capital letters then
    seven digits, for example HOM1234567). Returns its status, cover dates, covered perils and
    excess. Use it to check whether a claim is covered."""
    if not POLICY_NUMBER.fullmatch(policy_number):
        raise ToolError("Policy numbers are three capital letters then seven digits, for example HOM1234567.")
    policies = load("policies.json")
    if policy_number not in policies:
        raise ToolError(f"No policy {policy_number}. Take the policy number from get_claim instead of guessing.")
    return {"policy_number": policy_number, **policies[policy_number]}


@mcp.tool()
def update_claim_status(
    claim_id: str, status: Literal["APPROVED", "DECLINED", "REFERRED"], reason: str
) -> dict:
    """Set a claim's status to APPROVED, DECLINED or REFERRED, with a reason for the audit trail."""
    claims = load("claims.json")
    if claim_id not in claims:
        raise ToolError(f"No claim {claim_id}. Claim IDs look like CLM-1001; check the ID on the ticket.")
    claims[claim_id].update(status=status, status_reason=reason)
    (DATA / "claims.json").write_text(json.dumps(claims, indent=2) + "\n")
    return {"claim_id": claim_id, "status": status}


if __name__ == "__main__":
    mcp.run()  # stdio: the client starts this process and speaks JSON-RPC over stdin/stdout
