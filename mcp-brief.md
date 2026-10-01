# MCP in more depth: the coach's brief

For you, not the slides. It carries on from week 1's slide 9 row "Tools / MCP: when the agent calls
them: context in other systems", and covers what you need to answer questions in week 2 without
guessing.

## The sentence to get right

MCP is a **protocol**: an agreed JSON-RPC message format between an AI app and the programs that give it
capabilities. An **MCP server** is a program that speaks it and exposes **tools** (and optionally
resources and prompts). The **host** (VS Code with Copilot, Codex, Claude) runs an MCP **client** for each
server, turns the server's tools into the model's normal tool format, and makes the calls. "MCP is a
server" is a category error, like calling a website "HTTP".

## One call, end to end

Using week 2's server and "Why is CLM-1002 stuck?":

| Step | Who | What happens |
| --- | --- | --- |
| 1 | Host | Starts `python server.py` as a subprocess (stdio) and asks `tools/list` |
| 2 | Server | Replies with each tool's `name`, `description`, `inputSchema` |
| 3 | Host | Sends the user's message plus those tools (in the provider's own tool format) to the model |
| 4 | Model | Returns a tool call: `get_claim(claim_id="CLM-1002")`. It does not execute anything |
| 5 | Host | Applies its approval policy, then sends `tools/call` to the server |
| 6 | Server | Runs the function and returns `content` blocks, with `isError` if it raised |
| 7 | Host | Appends the result to the conversation and calls the model again |

The model never speaks MCP. Everything MCP-specific happens between host and server. That is why one
server works with Copilot, Codex and Claude: each host does its own translation (Codex renames the tool
to `mcp__claims__get_claim` for its model).

## What a server can expose

| Primitive | Who decides to use it | Example |
| --- | --- | --- |
| Tools | The model (via the host) | `get_claim`, `update_claim_status` |
| Resources | The app or user attaches them | A schema file, a runbook page |
| Prompts | The user picks them | A "triage this claim" template |
| Skills (extension) | The model or the user | A `SKILL.md` plus supporting files, served by the system it describes |

Week 2 only uses tools.

**Skills over MCP** is an optional extension, `io.modelcontextprotocol/skills` (SEP-2640), marked Final
on 13 Sep 2026. It builds on Resources: `skills/list` and `skills/get` return each skill's frontmatter
and a manifest of its files with SHA-256 digests; the host fetches `SKILL.md` and supporting files with
`resources/read` only when needed. The host must verify every file against the manifest, re-ask for
approval if the manifest changes, tag loaded content with its server, and get explicit user approval
before a skill runs code or grants tools. It is the same `SKILL.md` format as week 1's
`.github/skills/`, but it ships with the service instead of being copied into each repo. Adoption (29 Sep
2026): the MCP site's client support table lists no mainstream IDE, VS Code Copilot included, and the
official SDKs, Python included, have open pull requests. Treat skill content from a server as untrusted
input, like tool output.

## Transports

- **stdio:** the host launches the server locally and talks over stdin and stdout, one JSON message per
  line. That's week 2. A `print()` in the server corrupts the stream; log to stderr.
- **Streamable HTTP:** the server is a web service at a URL; same messages. Use it for shared or hosted
  servers. The older HTTP+SSE transport is deprecated.

"MCP means remote" is wrong: stdio servers are local processes.

## Versions

| | 2025-11-25 and earlier | 2026-07-28 |
| --- | --- | --- |
| Start of a connection | `initialize`, then `notifications/initialized` | No handshake. Each request carries its protocol version and client capabilities in `_meta` |
| Server identity and versions | In the `initialize` reply | `server/discover` (servers must implement it; clients may call it) |
| Sessions over HTTP | Optional `Mcp-Session-Id` | Removed. Cross-call state goes in explicit handles passed as tool arguments |
| Server needs more input mid-call | Server-initiated requests | Result with `resultType: "input_required"`; the client retries with `inputResponses` |

What you'll actually see in the session: the Python SDK here is `mcp` 2.2.0 (upgraded 2026-09-30 from
1.27.2). Its server speaks 2026-07-28 and every earlier revision; the first request on a connection picks
the era, and the other era's requests are then refused on that connection. Its own `Client` probes
`server/discover` and negotiates 2026-07-28 by itself. Codex 0.158 has its 2026-07-28 support switched
off (the `mcp_2026_07_28` feature is "under development"), so it still sends the handshake, and the same
server answers. The Copilot CLI 1.0.89 already speaks 2026-07-28: recorded on 30 Sep, it opened with
`server/discover`, then `subscriptions/listen`, `tools/list` and `tools/call`, all with `_meta`, no
`initialize`. VS Code's own client wasn't checked; `wiretap.py` or the server's output log shows it. Teach "list the tools, then
call one", which holds for both, and treat the handshake as version detail.

`mcp` 2.x also changed the server API, which matters if the colleague copies a 1.x tutorial:

| `mcp` 1.x | `mcp` 2.x |
| --- | --- |
| `from mcp.server.fastmcp import FastMCP` | `from mcp.server.mcpserver import MCPServer` |
| Any exception's message reaches the model | Only `ToolError` (`mcp.server.mcpserver.exceptions`) does; anything else shows as "Error executing tool <name>" |
| `ClientSession` + `stdio_client` + `initialize()` | `Client(StdioServerParameters(...))`, no initialize call |
| `tool.inputSchema`, `result.isError` | `tool.input_schema`, `result.is_error` (the wire JSON is unchanged) |

## How hosts show tools to the model

- **Copilot in VS Code:** servers come from `.vscode/mcp.json` (top-level `servers`; a stdio entry has
  `type`, `command`, `args`, and optionally `env`, `envFile`, `cwd`). `${workspaceFolder}` and
  `${input:…}` variables work. A trust dialog appears the first time a server starts or its config
  changes (reset with **MCP: Reset Trust**).
- **Approvals in VS Code:** the default permission level is "Manual permissions". You can approve a call
  once or for the session, workspace or always. `chat.tools.global.autoApprove` turns every prompt off,
  and so does the "Allow all" level. VS Code can also let a tool's result enter the chat without review
  ("post-approval"); its docs say to "use caution with external data that might contain prompt
  injection".
- **Codex:** hides MCP tools behind a tool search by default. In one recorded run it answered a bare
  "What's the status of claim CLM-1001?" by searching the repo, never calling the claims tools.
- **Copilot CLI** (bundled with Copilot Chat in VS Code; `copilot -p` runs it headless): reads servers
  from `~/.copilot/mcp-config.json`, `.mcp.json` or `.github/mcp.json`, or `--additional-mcp-config`.
  It shows tools to the model up front as `claims-get_claim`; asked the same bare question, it called
  `get_claim` straight away. It also called `lookup_policy` in parallel with `get_claim` before it knew
  the policy number (4 of 4 triage runs), once reading a different customer's policy. A tool that needs
  an ID from another tool invites that guess; returning both together removes it.

## Security, the part that matters most for a claims team

1. **Tool output is untrusted input.** It lands in the same context as your instructions. Whoever wrote
   the data (a customer's free-text field, a colleague's ticket, a web page) is writing into your prompt.
2. **Tool descriptions are untrusted input too.** A third-party server's author writes text straight into
   your agent's context. Install servers the way you'd add a dependency.
3. **Annotations are hints.** `readOnlyHint`, `destructiveHint` and similar come from the server's author;
   nothing enforces them.
4. **The controls that hold don't depend on the model:** expose only the tools the task needs, approve
   writes yourself, enforce business rules in the server (week 2's lapsed-policy guard), and authorise on
   the server side. Having discovered a tool is not permission to use it.
5. **Data policy:** whatever a tool returns is sent to the model provider, exactly like a prompt.

Week 2 evidence (GPT-6-Luna via Codex, 9 planted runs): it never approved the claim, it changed its
answer in 2 runs, and in 5 of 6 triage runs it didn't mention that the customer tried. Details in
`session.md` Part 2.

## Questions the colleague may ask

| Question | Short answer |
| --- | --- |
| Isn't this just an API? | An MCP server usually wraps one. MCP is the standard way any agent finds and calls it, so you write the wrapper once. |
| Why not let the agent call our REST API directly? | It could with a bespoke tool per agent. MCP gives one integration that every host can use, plus descriptions shaped for a model rather than raw endpoints. |
| Does the model run my code? | No. The host runs your server; the model only asks for calls. |
| Does the server have to keep running? | Local (stdio): no, Copilot starts it when it needs the tools and stops it after. Remote (Streamable HTTP): yes, like any web API, but with no sessions since 2026-07-28 any copy can answer. Running `python server.py` yourself looks frozen: it's waiting for a client. |
| How does Copilot know where the tool is? | From `mcp.json`: a command for a local server, a URL for a remote one. Copilot starts the server and lists its tools before the model sees anything; the model only sees names like `claims-get_claim`, and the prefix routes each call back. |
| Can Copilot call it without asking? | Only if approvals are relaxed: an "always" approval, `chat.tools.global.autoApprove`, or "Allow all". |
| Does our data go to the model? | Yes: whatever the tool returns, like a prompt. |
| How does it know which tool to use? | From the name, description and input schema, plus your prompt. Next week opens that loop. |
| Where would we use this for real? | Read-only lookups first: tickets, schemas, test data, runbooks. Writes last, behind approvals. |

## Sources (checked 2026-09-29)

- MCP 2026-07-28 changelog: <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
- Skills over MCP: <https://modelcontextprotocol.io/extensions/skills/overview>; client support:
  <https://modelcontextprotocol.io/extensions/client-matrix>
- VS Code MCP servers: <https://code.visualstudio.com/docs/copilot/customization/mcp-servers>
- VS Code MCP configuration reference: <https://code.visualstudio.com/docs/copilot/reference/mcp-configuration>
- VS Code approvals: <https://code.visualstudio.com/docs/agents/run/approvals>
- VS Code enterprise AI settings: <https://code.visualstudio.com/docs/enterprise/ai-settings>
- GitHub, "MCP servers in Copilot" policy: <https://docs.github.com/en/copilot/concepts/context/mcp>
- GitHub changelog, default enablement from 22 Oct 2026:
  <https://github.blog/changelog/2026-09-24-default-enablement-of-copilot-features-for-copilot-business-and-enterprise/>
