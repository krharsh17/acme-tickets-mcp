import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes
from fastmcp.server.auth.providers.descope import DescopeProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("acme-tickets")

PROJECT_ID = os.environ["DESCOPE_PROJECT_ID"]
MCP_SERVER_ID = os.environ["DESCOPE_MCP_SERVER_ID"]
MCP_SERVER_URL = os.environ["MCP_SERVER_URL"]  # e.g. https://tickets.example.com/mcp
ISSUER = f"https://api.descope.com/v1/apps/agentic/{PROJECT_ID}/{MCP_SERVER_ID}"

# Accept only tokens that Descope minted for this MCP server
verifier = JWTVerifier(
    jwks_uri=f"https://api.descope.com/{PROJECT_ID}/.well-known/jwks.json",
    issuer=ISSUER,
    audience=MCP_SERVER_URL,
    algorithm="RS256",
)

auth = DescopeProvider(
    config_url=f"{ISSUER}/.well-known/openid-configuration",
    base_url=os.environ["BASE_URL"],
    scopes_supported=["tickets:read", "tickets:write"],
    token_verifier=verifier,
)

mcp = FastMCP(name="Acme Tickets", auth=auth)

TICKETS = {
    4821: {"title": "CSV export fails on large files", "status": "open", "fixed_in": "v2.14.1"},
    4822: {"title": "SSO login loops on Safari", "status": "open", "fixed_in": None},
}


@mcp.tool(auth=require_scopes("tickets:read"))
def get_ticket(ticket_id: int) -> dict:
    """Fetch a support ticket by ID."""
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket {ticket_id} not found")
    return {"id": ticket_id, **ticket}


@mcp.tool(auth=require_scopes("tickets:write"))
def close_ticket(ticket_id: int, resolution: str) -> dict:
    """Close a support ticket with a resolution note."""
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket {ticket_id} not found")
    ticket["status"] = "closed"
    claims = get_access_token().claims
    logger.info("close_ticket id=%s user=%s scopes=%s", ticket_id, claims["sub"], claims.get("scope"))
    return {"id": ticket_id, "status": "closed", "resolution": resolution}


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)