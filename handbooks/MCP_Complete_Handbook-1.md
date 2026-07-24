# The MCP Complete Handbook
### A Beginner-to-Medium Guide to the Model Context Protocol

---

## Table of Contents

1. What is MCP? (Simple Analogy)
2. Why MCP Was Created
3. Core Building Blocks
4. Client vs Server
5. What Servers Provide
6. How Communication Works
7. Claude Desktop Architecture
8. ChatGPT + MCP
9. Cursor + MCP
10. IntelliJ MCP Plugin
10a. Your Setup: Claude Desktop + IntelliJ MCP Plugin
11. GitHub MCP
12. Filesystem MCP
13. PostgreSQL MCP
14. Outlook MCP
15. OneDrive MCP
16. Setting Up Your First Server
17. Basic Security Concepts
18. Troubleshooting & Tools
19. Hands-On Lab: Build a Simple MCP Client + Server (Mac, Python, Free LLM)
20. Where to Go Next

---

## 1. What is MCP? (Simple Analogy)

**MCP (Model Context Protocol)** is an open standard that lets AI applications (like Claude, ChatGPT, or a code editor) connect to external tools, files, and data sources in a consistent way.

**Simple analogy: USB-C for AI apps.**

Before USB-C, every device had its own charger and cable. Once USB-C became standard, any device could plug into any charger. MCP does the same thing for AI:

- Without MCP: every AI app needs its own custom code to talk to Slack, GitHub, a database, etc.
- With MCP: one "MCP server" for GitHub can be plugged into Claude, ChatGPT, Cursor, or any other MCP-compatible app — no rewriting needed.

**One-line definition:**
> MCP is a standard protocol that lets an AI model ask an external program for tools, data, or prompt templates, using a shared set of rules everyone agrees on.

**Everyday example:**
Imagine you ask Claude, "What's the weather in Tokyo?" Claude doesn't know real-time weather. But if Claude is connected to a Weather MCP server, it can:
1. Recognize it needs live data.
2. Call the weather server's `get_weather` tool.
3. Get the result back and answer you.

---

## 2. Why MCP Was Created

**The problem: the "N×M problem."**

Imagine there are:
- N = AI applications (Claude, ChatGPT, Cursor, IntelliJ, custom agents…)
- M = tools/data sources (GitHub, Slack, databases, file systems, email…)

Without a shared standard, you need a custom integration for every AI app × every tool combination. That's N × M separate integrations — expensive and hard to maintain.

**The solution: a shared protocol.**

If every tool provider builds ONE MCP server, and every AI app builds ONE MCP client, then any app can use any tool. The math becomes N + M instead of N × M.

**Example:**
- GitHub builds one MCP server for its API.
- Claude Desktop, Cursor, and IntelliJ each build MCP client support once.
- Now all three apps can use GitHub — without GitHub building three separate integrations, and without each app building custom GitHub code.

**Other goals of MCP:**
- Open standard (not tied to one company)
- Security and consent built in (user approves what tools can do)
- Works locally (on your machine) or remotely (over the internet)
- Simple enough that small tools and large enterprise systems can both use it

---

## 3. Core Building Blocks

MCP has three main roles:

| Role | What it is | Example |
|---|---|---|
| **Host** | The AI application the user interacts with | Claude Desktop, ChatGPT, Cursor |
| **Client** | The connector inside the host that talks to a server | Built into the host app |
| **Server** | The program that exposes tools, data, or prompts | A GitHub MCP server, a filesystem MCP server |

**Simple flow diagram:**

![Host, Client, and Server flow](images/diagram1_host_client_server.png)

**Example in plain terms:**
You ask Claude Desktop: "List my open GitHub issues."
- Host = Claude Desktop app
- Client = the MCP connector inside Claude Desktop
- Server = the GitHub MCP server, which actually calls GitHub's API

---

## 4. Client vs Server

**What the Client does:**
- Lives inside the host application
- Discovers what tools/resources a server offers ("capability discovery")
- Sends requests to the server ("call this tool with these arguments")
- Receives results and passes them back to the AI model
- Manages the connection (open, close, reconnect)

**What the Server does:**
- Defines and exposes **tools** (actions), **resources** (data), and **prompts** (templates)
- Validates incoming requests
- Executes the actual logic (e.g., querying a database, reading a file)
- Returns structured results to the client

**Who owns trust and permissions:**
- The **host** typically asks the **user** for permission before a tool runs (e.g., "Allow Claude to read this file?")
- The **server** should only do what it's scoped to do (e.g., a "read-only" filesystem server should never delete files)
- The **client** should never blindly trust server output — treat it like untrusted external data

**Simple example:**
- Client: "Do you have a tool called `search_issues`?"
- Server: "Yes, here's its schema: it takes a `query` string and returns a list of issues."
- Client: "Please run `search_issues` with query = 'bug'."
- Server: runs the search, returns 5 matching issues.
- Client: hands those 5 issues to the AI model to summarize for the user.

---

## 5. What Servers Provide

MCP servers can expose three types of things:

### Tools
Actions the AI model can actively call, like functions.
**Example:** `send_email(to, subject, body)`, `create_github_issue(title, description)`

### Resources
Read-only data the model or user can access, like files or documents.
**Example:** A resource could be `file:///project/README.md`, or a URI like `github://repo/issues/42`

### Prompts
Reusable prompt templates the server provides, so users/apps don't have to write them from scratch.
**Example:** A "code review" prompt template that formats a diff and asks specific review questions.

**Quick comparison table:**

| Type | Purpose | Example |
|---|---|---|
| Tool | Perform an action | `create_calendar_event()` |
| Resource | Provide data | A PDF, log file, or database row |
| Prompt | Reusable instructions | "Summarize this meeting transcript in 3 bullet points" |

![Tools, Resources, and Prompts](images/diagram3_tools_resources_prompts.png)

---

## 6. How Communication Works

**JSON-RPC basics.**
MCP messages use JSON-RPC 2.0 — a simple format for requests and responses.

Example request (simplified):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": { "city": "Tokyo" }
  }
}
```

Example response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "temperature": "24°C",
    "condition": "Cloudy"
  }
}
```

**Local vs remote servers:**

| Type | Transport | Example use |
|---|---|---|
| Local | stdio (standard input/output) | A filesystem server running on your own machine |
| Remote | HTTP / Server-Sent Events (SSE) | A cloud-hosted Slack or GitHub MCP server |

![Local vs remote server](images/diagram4_local_vs_remote.png)

**Simple walkthrough:**
1. Host starts the server (locally) or connects to it (remotely).
2. Client and server "handshake" — they exchange what capabilities each supports.
3. Client asks: "What tools do you have?"
4. Server replies with a list of tools and their input/output schemas.
5. When needed, client calls a tool; server executes it and returns a result.

---

## 7. Claude Desktop Architecture

Claude Desktop is one of the most common ways people first use MCP.

**How it works:**
- Claude Desktop acts as the **Host**.
- It has a built-in **Client** that manages connections to MCP servers.
- You configure servers in a config file (`claude_desktop_config.json`), specifying how to launch each server (usually a local command).

![Claude Desktop architecture](images/diagram2_claude_desktop.png)

**Example config snippet:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/Documents"]
    }
  }
}
```

**What happens when you restart Claude Desktop:**
1. Claude Desktop reads the config file.
2. It launches each configured server as a local process (via stdio).
3. It performs the capability handshake with each server.
4. Tools from all connected servers become available inside your chat.
5. When the AI decides to use a tool, Claude Desktop shows a permission prompt before running it.

**Key point:** Claude Desktop mostly runs servers **locally** on your computer, which is why file system and local app integrations (like note apps) are common first examples.

---

## 8. ChatGPT + MCP

ChatGPT has been rolling out support for connecting to external tools using protocols compatible with MCP-style concepts, primarily through its "Connectors" and "Actions" framework rather than a native "MCP client" label in the same sense as Claude Desktop.

**How it's similar to MCP:**
- Both let a model call external tools with structured input/output.
- Both use a permission/consent step before running sensitive actions.

**How it differs:**
- ChatGPT's connector ecosystem has historically been built around its own Actions/plugin schema, with MCP-compatible support expanding over time.
- Enterprise ChatGPT deployments increasingly support connecting to MCP servers for internal tools and data.

**Simple example use case:**
A company connects ChatGPT to an internal MCP-compatible server exposing "search internal wiki" and "create support ticket" tools, so employees can ask ChatGPT questions that pull from internal systems.

*Because this area evolves quickly, always check current documentation for the latest ChatGPT + MCP support details before building something in production.*

---

## 9. Cursor + MCP

**Cursor** is an AI-powered code editor (a fork of VS Code) that supports MCP servers directly.

**Why this matters for developers:**
- You can connect Cursor to tools like GitHub, a database, or a documentation search server.
- The AI coding assistant inside Cursor can then use those tools while helping you code — e.g., checking a database schema before writing a query.

**Example setup:**
In Cursor's settings, you add an MCP server (similar JSON config style to Claude Desktop):
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

**Example use case:**
While writing a backend function, you ask Cursor: "What columns does the `users` table have?" Cursor's AI calls the Postgres MCP server's schema tool and answers accurately instead of guessing.

---

## 10. IntelliJ MCP Plugin

JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.) support MCP through a dedicated plugin that connects the IDE's AI assistant to MCP servers.

**What it enables:**
- The AI assistant inside IntelliJ can call external MCP tools (e.g., GitHub, filesystem, database servers) directly from the IDE.
- Developers can keep using their existing IDE workflow while gaining access to external context (like ticket details or repo issues) without switching windows.

**Example use case:**
A developer working on a bug fix asks the IntelliJ AI assistant: "Show me the GitHub issue related to this file." With the GitHub MCP server connected, the assistant fetches issue details and displays them right inside the IDE.

**Setup pattern:**
Similar to other hosts — you install the plugin, then register MCP servers (often via a settings panel or config file) so the IDE can launch and connect to them.

---

## 10a. Your Setup: Claude Desktop + IntelliJ MCP Plugin

Since you're running **Claude Desktop connected to IntelliJ via the MCP plugin**, here's exactly what each component is and where it runs, in plain terms.

**The key idea:** in this setup, Claude Desktop and IntelliJ are BOTH running on your own computer — nothing goes to a remote server for this connection. They talk to each other locally.

| Component | Role in MCP terms | Where it runs | What it does |
|---|---|---|---|
| **Claude Desktop** | **Host + Client** | On your computer, as its own app | This is what you type into. It contains the MCP client, which is the part that reaches out and connects to servers. |
| **IntelliJ IDEA + MCP Plugin** | **Server** | On your computer, inside/alongside the IDE | The plugin turns your IDE into an MCP server. It exposes tools such as reading the currently open file, browsing your project structure, or running code — Claude can call these. |
| **You (the developer)** | **User** | In front of your screen | You ask Claude a question; you also approve permission prompts before a tool runs. |

**Why it's set up this way:**
IntelliJ already knows everything about your project — open files, project structure, run configurations, the code index. Rather than Claude Desktop trying to read your disk directly and guess which project you mean, the IntelliJ plugin exposes that IDE context *as MCP tools*, so Claude can ask for exactly what it needs (e.g., "what's in the currently open file?") through a well-defined interface.

**Step-by-step walkthrough of what happens when you ask Claude something in this setup:**
1. You type a question in Claude Desktop, e.g., "What does the `UserService` class in my open project do?"
2. Claude Desktop (**Host**) realizes it needs IDE context and its built-in **Client** sends a request over the MCP connection.
3. The **IntelliJ MCP plugin (Server)** receives the request, looks at the actual project open in your IDE, and runs the matching tool (e.g., `get_file_contents` or similar).
4. The plugin sends the result back to Claude Desktop's client.
5. Claude Desktop's AI model reads that result and writes you an answer, grounded in your real code — not a guess.

**Where things physically live:**
- Both processes run locally on your machine.
- The connection between them is a **local transport** (similar to the stdio/local-socket pattern described in Section 6 — not over the public internet).
- No cloud server is involved unless you've also connected a remote MCP server (like Outlook or OneDrive) separately.

![Your Claude Desktop + IntelliJ setup](images/diagram5_your_setup.png)

**Quick way to verify this yourself:**
- In IntelliJ, check the plugin's settings/status panel — it usually shows "MCP server running" along with a port or connection status.
- In Claude Desktop, check Settings → Developer/MCP section — it should list IntelliJ (or the plugin's server name) as a connected server, along with the tools it exposes.
- If you ask Claude something IDE-specific and it responds with accurate details about your actual open project, that confirms the client-server connection is working.

---

## 11. GitHub MCP

The **GitHub MCP server** exposes GitHub functionality as tools and resources.

**Common tools it might provide:**
- `search_issues(query)` — search issues across repos
- `create_issue(repo, title, body)` — open a new issue
- `list_pull_requests(repo)` — see open PRs
- `get_file_contents(repo, path)` — read a file from a repo

**Example use case:**
You ask: "Create a GitHub issue in my `web-app` repo titled 'Fix login bug' with a description of the steps to reproduce."
The AI calls `create_issue` with those arguments, and the server creates the issue via GitHub's API, returning a link back to you.

**Why it's useful:**
Instead of switching to GitHub's website, you manage repos conversationally, directly from Claude, Cursor, or another connected host.

---

## 12. Filesystem MCP

The **Filesystem MCP server** lets an AI read (and optionally write) files on your local machine, within a scope you define.

**Common tools it might provide:**
- `read_file(path)`
- `write_file(path, content)`
- `list_directory(path)`
- `search_files(query)`

**Example use case:**
You ask: "Summarize all the meeting notes in my `Notes/2026` folder."
The AI calls `list_directory`, then `read_file` on each note, and produces a summary — all without you copy-pasting content manually.

**Important safety note:**
Filesystem servers are usually configured with a specific root folder (e.g., only `/Users/you/Documents`) so the AI can't accidentally read or modify files outside that scope.

---

## 13. PostgreSQL MCP

The **PostgreSQL MCP server** allows an AI to query a Postgres database safely, often in read-only mode by default.

**Common tools it might provide:**
- `list_tables()`
- `describe_table(table_name)`
- `run_query(sql)` — often restricted to `SELECT` statements only

**Example use case:**
You ask: "How many orders were placed last month?"
The AI calls `run_query` with a safe `SELECT COUNT(*) FROM orders WHERE ...` statement, and the server returns the number.

**Why read-only matters:**
Most Postgres MCP setups intentionally block `INSERT`, `UPDATE`, and `DELETE` statements to prevent an AI mistake (or a prompt injection) from damaging your data.

---

## 14. Outlook MCP

The **Outlook MCP server** connects an AI to your email and calendar through Microsoft's ecosystem.

**Common tools it might provide:**
- `list_emails(folder, filter)`
- `send_email(to, subject, body)`
- `create_calendar_event(title, start_time, end_time)`
- `search_emails(query)`

**Example use case:**
You ask: "Find the email from my manager about the Q3 budget and summarize it."
The AI calls `search_emails`, retrieves the matching message, and gives you a short summary — without you opening Outlook.

**Security note:**
Because email access is sensitive, Outlook MCP servers typically require OAuth authentication and often ask for explicit confirmation before sending any email on your behalf.

---

## 15. OneDrive MCP

The **OneDrive MCP server** gives an AI access to files stored in Microsoft OneDrive (similar in spirit to the Filesystem server, but for cloud storage).

**Common tools it might provide:**
- `list_files(folder)`
- `read_file(file_id)`
- `search_files(query)`
- `upload_file(folder, content)`

**Example use case:**
You ask: "Find my latest project proposal in OneDrive and pull out the budget section."
The AI searches OneDrive, opens the matching document, and extracts the relevant section for you.

**Why this matters:**
It lets AI assistants work with your existing cloud documents without you needing to download, upload, or copy-paste content manually.

---

## 16. Setting Up Your First Server

Here's a simplified example of building a minimal MCP server (conceptually, using the Python SDK).

**Step 1: Install the SDK**
```bash
pip install mcp
```

**Step 2: Write a simple tool**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

**Step 3: Run it locally**
```bash
python calculator_server.py
```

**Step 4: Connect it to a host**
Add it to your host's config (e.g., Claude Desktop's `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["/path/to/calculator_server.py"]
    }
  }
}
```

**Step 5: Test it**
Restart the host app, then ask: "What's 42 plus 58?" The AI should call your `add` tool and return 100.

---

## 17. Basic Security Concepts

**Why permissions matter:**
MCP servers can take real actions (send emails, delete files, run SQL). Without safeguards, a mistake or malicious input could cause real harm.

**Key practices:**
- **User approval before running tools** — hosts typically show a confirmation dialog the first time (or every time) a tool is used.
- **Scoping access** — give servers the minimum access they need (e.g., a single folder, read-only database access).
- **Not trusting server output blindly** — treat data returned by a server as untrusted input, especially if it comes from external sources like the web or emails, since it could contain hidden instructions ("prompt injection").
- **Authentication** — remote servers (like Outlook or OneDrive) typically require OAuth login, not shared passwords.

**Simple example of a risk:**
If a Filesystem MCP server has write access to your entire hard drive instead of one folder, an AI mistake (or a manipulated prompt) could overwrite important files. Scoping to one folder limits the blast radius.

---

## 18. Troubleshooting & Tools

**MCP Inspector** is an official tool for testing and debugging MCP servers without needing a full host app.

**What you can do with it:**
- Connect to a server directly and see its available tools, resources, and prompts.
- Manually send test requests and see raw responses.
- Check for schema errors before connecting the server to a real host.

**Common errors and fixes:**

| Error | Likely Cause | Fix |
|---|---|---|
| Server won't start | Wrong command/path in config | Double-check config file paths |
| "Tool not found" | Client cached old capability list | Restart the host app |
| Permission denied | Server scope too narrow, or missing OAuth | Check server config and re-authenticate |
| Timeout | Server hanging or slow external API call | Add logging to the server to find where it's stuck |
| JSON parse error | Malformed response from server | Validate your server's JSON output matches the schema |

---

## 19. Hands-On Lab: Build a Simple MCP Client + Server (Mac, Python, Free LLM)

This is a complete, working mini-project: a **server** that gives an AI read-only access to a folder of `.txt` files on your Mac, and a **client** that connects a **free, local LLM** (via [Ollama](https://ollama.com)) to that server. No API keys, no paid accounts.

### What you'll build

![Hands-on lab architecture](images/diagram6_hands_on_lab.png)

- `server.py` — an MCP server exposing two tools: `list_files()` and `read_file(filename)`, scoped to one folder.
- `client.py` — an MCP client that launches the server, asks a local LLM a question, lets the LLM call tools if needed, and prints the answer.
- **Ollama**, running a free open-source model (e.g. `llama3.1`) entirely on your own machine.

### Step 1 — Install prerequisites

```bash
# Python MCP SDK + HTTP library
pip install mcp requests

# Ollama (free, local LLM runner)
brew install ollama
ollama pull llama3.1        # any tool-calling-capable model works
```

Ollama runs a local server at `http://localhost:11434` — that's the "free LLM" this lab uses. No internet call, no API key, no cost.

### Step 2 — Create a folder of notes

```bash
mkdir -p ~/Documents/mcp_notes
echo "Grocery list: eggs, milk, spinach, coffee." > ~/Documents/mcp_notes/note1.txt
echo "Project idea: build a home budget tracker in Python." > ~/Documents/mcp_notes/note2.txt
```

This is the folder your MCP server will be scoped to — the AI can only see files in here, nothing else on your Mac.

### Step 3 — The MCP Server (`server.py`)

```python
"""
server.py — a tiny MCP server that gives read-only access
to a folder of .txt files on your Mac.
"""

import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# CHANGE THIS to whatever folder you want the AI to read from.
ALLOWED_DIR = Path(os.path.expanduser("~/Documents/mcp_notes")).resolve()
ALLOWED_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("Notes Folder Server")


@mcp.tool()
def list_files() -> list[str]:
    """List all .txt files available in the notes folder."""
    return [f.name for f in ALLOWED_DIR.glob("*.txt")]


@mcp.tool()
def read_file(filename: str) -> str:
    """Read the full contents of one .txt file from the notes folder.

    Args:
        filename: the name of the file, e.g. 'note1.txt'
    """
    target = (ALLOWED_DIR / filename).resolve()

    # Safety check: never allow escaping the allowed folder.
    if not str(target).startswith(str(ALLOWED_DIR)):
        return "Error: access outside the notes folder is not allowed."
    if not target.exists():
        return f"Error: '{filename}' was not found in the notes folder."

    return target.read_text(encoding="utf-8", errors="ignore")


if __name__ == "__main__":
    mcp.run()
```

**Why the safety check matters:** without the `startswith` check, someone could ask for `filename="../../../etc/passwd"` and read files way outside the notes folder. Always scope and validate paths in a real server.

### Step 4 — The MCP Client (`client.py`)

```python
"""
client.py — a minimal MCP client that:
  1. Launches server.py and connects to it over MCP (stdio)
  2. Asks a free, local LLM (via Ollama) a question
  3. Lets the LLM call MCP tools (list_files / read_file) if it needs to
  4. Prints the final answer
"""

import asyncio
import requests

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1"


def mcp_tool_to_ollama_tool(tool) -> dict:
    """Convert an MCP tool definition into the JSON shape Ollama expects."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def main():
    question = input("Ask something about your notes folder: ")

    # 1. Launch the local MCP server as a subprocess and connect to it.
    server_params = StdioServerParameters(command="python3", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 2. Discover what tools the server offers.
            tools_response = await session.list_tools()
            ollama_tools = [mcp_tool_to_ollama_tool(t) for t in tools_response.tools]

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You can answer questions about text files using the "
                        "provided tools. Always call list_files first if you "
                        "are not sure which file to read."
                    ),
                },
                {"role": "user", "content": question},
            ]

            # 3. Ask the local LLM, giving it the MCP tools as options.
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "messages": messages, "tools": ollama_tools, "stream": False},
                timeout=120,
            ).json()

            msg = response["message"]

            # 4. If the model wants to call a tool, run it via the MCP server.
            if msg.get("tool_calls"):
                messages.append(msg)

                for call in msg["tool_calls"]:
                    tool_name = call["function"]["name"]
                    tool_args = call["function"]["arguments"]

                    print(f"  -> calling MCP tool: {tool_name}({tool_args})")
                    result = await session.call_tool(tool_name, tool_args)
                    tool_text = result.content[0].text

                    messages.append({"role": "tool", "content": tool_text})

                # 5. Send the tool result(s) back so the model can write a final answer.
                final = requests.post(
                    OLLAMA_URL,
                    json={"model": MODEL, "messages": messages, "stream": False},
                    timeout=120,
                ).json()
                print("\n" + final["message"]["content"])
            else:
                # Model answered directly without needing a tool.
                print("\n" + msg["content"])


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 5 — Run it

```bash
python3 client.py
```

Try asking:
- `"What files do I have?"` → model calls `list_files()`
- `"What's on my grocery list?"` → model calls `list_files()`, figures out which file, then calls `read_file("note1.txt")`

### What's happening under the hood (mapped to earlier sections)

| Piece | MCP role | Section to review |
|---|---|---|
| `client.py` | Client (and also the Host, since there's no separate app wrapping it here) | Section 3–4 |
| `server.py` | Server | Section 3–5 |
| `list_files`, `read_file` | Tools | Section 5 |
| stdio connection between client and server | Local transport | Section 6 |
| the `startswith` check in `read_file` | Scoping / security | Section 17 |
| Ollama | The "brain" deciding when to call a tool — not part of MCP itself, just the LLM you plug in | — |

### Notes and troubleshooting

- If `ollama pull llama3.1` is too large/slow, smaller tool-calling models (check Ollama's model library) work too — the code doesn't change, just the `MODEL` variable.
- If tool calls aren't triggering, confirm your chosen model supports tool/function calling — not all local models do.
- This lab intentionally keeps orchestration manual (no agent framework) so you can see every MCP request/response directly. Add `print(response)` after any API call to inspect the raw JSON.
- Exact Ollama and MCP SDK APIs evolve — if a call errors, check the current docs for `ollama` (`ollama.com`) and the `mcp` Python package for any signature changes.

---

## 20. Where to Go Next

**Official resources:**
- MCP official documentation and specification
- SDKs for Python, TypeScript, and other languages
- Official example servers (filesystem, GitHub, Postgres, etc.) as reference implementations

**Suggested learning path:**
1. Install Claude Desktop or Cursor and connect an existing MCP server (like Filesystem or GitHub).
2. Use MCP Inspector to explore how a server's tools are structured.
3. Build your own minimal server (like the calculator example above).
4. Add a real-world tool — e.g., a weather API, a to-do list, or a simple database query tool.
5. Explore security scoping and OAuth once you're comfortable with the basics.

**Small project ideas to practice:**
- A "notes" MCP server that reads/writes a local markdown notes folder.
- A "task tracker" MCP server backed by a simple SQLite database.
- A "weather" MCP server that wraps a public weather API.

---

*End of Handbook*
