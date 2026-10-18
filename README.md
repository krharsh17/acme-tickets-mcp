# Acme Tickets: example MCP server with Descope auth

A minimal remote MCP server (`server.py`) used as the companion code for a set of tutorials on adding OAuth-based authorization to an MCP server with [Descope](https://www.descope.com/), each federating to a different identity provider:

- Okta
- Auth0
- Amazon Cognito
- Microsoft Entra ID

## Why one server works for all four

The server never talks to your identity provider directly. It only validates access tokens issued by Descope, which acts as the MCP server's OAuth 2.1 authorization server and handles discovery, client registration, consent, and token issuance. The identity provider federation (Okta, Auth0, Cognito, or Entra ID) happens entirely on the Descope side, through a tenant SSO connection.

That means `server.py` is identical across every tutorial in this series. Only the IdP-specific setup, the SSO connection, group or role claim mapping, and the consent flow wiring, changes depending on which identity provider you're following along with.

## What it exposes

A small support desk with two tools of different sensitivity:

- `get_ticket`, requires the `tickets:read` scope
- `close_ticket`, requires the `tickets:write` scope

The scope split gives each tutorial something concrete to gate behind a user's role or group membership in the identity provider.

## Prerequisites

- Python 3.10 or later
- A [Descope account](https://www.descope.com/sign-up) (the Free Forever plan covers these tutorials)
- An HTTPS URL for the server, such as a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/) pointing at your machine

## Setup

```bash
pip install "fastmcp>=4" python-dotenv
cp .env.example .env
```

The server needs a public HTTPS URL for Descope and your IdP to reach it. In one terminal, point a tunnel at port 8000, the port the server listens on:

```bash
cloudflared tunnel --url http://localhost:8000
```

Use the HTTPS URL `cloudflared` prints as `MCP_SERVER_URL`/`BASE_URL` in `.env`, alongside your Descope project and MCP server IDs (the IdP-specific tutorial you're following covers where to get those). It changes on every restart unless you're on a paid Cloudflare plan with a reserved domain, so if you restart the tunnel, update `.env` and re-register the new URL wherever your IdP tutorial has you configure a redirect or callback URL.

In another terminal, start the server:

```bash
python server.py
```

## Repo contents

- `server.py`, the MCP server itself
- `.env.example`, the environment variables the server expects

This repo intentionally doesn't include IdP-specific configuration, that lives in each tutorial's own setup steps, since it's the one part that actually differs between Okta, Auth0, Cognito, and Entra ID.
