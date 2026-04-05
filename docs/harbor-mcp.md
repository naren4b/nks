![https://github.com/naren4b/harbor-mcp/blob/main/mcp-harbor.jpg](https://github.com/naren4b/harbor-mcp/blob/main/mcp-harbor.jpg)

# Harbor MCP — Talk to Your Container Registry in Plain English

> Ask questions like *"Show me all repositories in project demo"* and get real answers —
> powered by a local AI model talking directly to your Harbor registry.
> Everything runs on your own laptop. No cloud. No subscriptions.

---

## What Is This?

[Harbor](https://goharbor.io/) is a popular open-source container image registry used by teams
to store and manage Docker images. Normally you manage it through a web UI or write scripts.

This project lets you **ask plain English questions** about your Harbor registry and get real,
live answers. It works by connecting a local AI (running via [Ollama](https://ollama.com/))
to Harbor through the **Model Context Protocol (MCP)**.

```
You  ──►  MCP Client  (src/client/main.py)
               │
               │  subprocess over stdio
               ▼
          MCP Server  (src/server/harbor-mcp-server.py)
               │
               │  HTTPS REST API
               ▼
          Harbor Registry  (your instance)
```

The AI brain (Ollama) lives inside the client. The MCP server is a lean tool-router
that knows how to speak Harbor's API. They talk to each other over a local subprocess —
no network ports needed between them.

---

## What Can You Ask?

Three tools are available today. The AI picks the right one automatically based on your question.

| Tool | What it does | Example question you can ask |
|---|---|---|
| `getProjects` | List all projects in the registry | *"What projects are in Harbor?"* |
| `getRepositories` | List repositories inside a project | *"Show repositories in project demo"* |
| `getArtifacts` | List artifacts (images + tags) in a repository | *"What tags exist for my-alpine in demo?"* |

---

## What You Need Before Starting

### 1. Python 3.12 or newer
```bash
python3 --version   # should print 3.12.x or higher
```
If it's older, download from [python.org/downloads](https://www.python.org/downloads/).

### 2. uv — the package manager this project uses
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
uv --version   # confirm it installed
```

### 3. Ollama — runs the AI model locally on your machine
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Start it:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
```
Pull a model that supports **tool calling** (this is required for MCP to work):
```bash
OLLAMA_MODEL=minimax-m2.7:cloud
ollama pull $OLLAMA_MODEL
ollama run $OLLAMA_MODEL   # quick sanity check — type 'hello' and hit Enter
```

### 4. A Harbor Registry you can reach
This can be:
- Your company's Harbor instance (`https://registry.yourcompany.com`)
- A locally running Harbor via Docker Compose — see the [Harbor install guide](https://goharbor.io/docs/latest/install-config/)

You just need a username and password that has at least **Guest** access to the projects you want to query.

---

## Project Layout

```
harbor-mcp/
├── pyproject.toml                  # all Python dependencies live here
├── src/
│   ├── .env.example                # template — copy this to src/.env and fill in your values
│   ├── client/
│   │   ├── main.py                 # entry point — run this to start the chat
│   │   └── MCPClient.py            # manages the Ollama conversation and MCP tool calls
│   └── server/
│       ├── harbor-mcp-server.py    # MCP server — wraps Harbor API as callable tools
│       └── harbor.py               # raw Harbor API layer (uses the harborapi library)
```

---

## MCP Test Client

```bash
git clone git@github.com:naren4b/harbor-mcp.git
cd harbor-mcp
uv venv
source .venv/bin/activate
uv sync 
cp src/.env.example src/.env 
vi src/.env   # update the Harbor and LLM configuration (see below)
uv run src/client/main.py src/server/harbor-mcp-server.py
```

---

## Configuration — src/.env

Open `src/.env` and fill in your values. Here is what each setting means:

```ini
# --- Harbor Registry ---
HARBOR_NAME=registry-name              # friendly name, used for display only
HARBOR_URL=https://registry.yourcompany.com   # base URL of your Harbor instance
HARBOR_USERNAME=your-username          # Harbor login username
HARBOR_PASSWORD=your-password          # Harbor login password
INSECURE_SKIP_TLS_VERIFY=false         # set to true if your cert is self-signed

# --- Local AI (Ollama) ---
OLLAMA_MODEL=minimax-m2.7:cloud        # must be a model that supports tool calling
OLLAMA_HOST=http://127.0.0.1:11434     # default Ollama address — change only if needed
```

> **Your credentials are safe.** The `src/.env` file is listed in `.gitignore` and will
> never be accidentally committed to git.

---

## LLM Setup (Quick Reference)

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
OLLAMA_MODEL=minimax-m2.7:cloud
ollama pull $OLLAMA_MODEL
ollama run $OLLAMA_MODEL
```

---

## Optional — Test Harbor Connectivity First

Before running the full AI chat, you can verify your credentials and Harbor reachability
directly using the standalone `harbor.py` script:

```bash
# show all repositories in a project
python src/server/harbor.py --project-name=your-project-name

# show artifacts in a specific repository
python src/server/harbor.py --project-name=your-project-name --repository-name=your-repo-name
```

If repository data is printed, your `.env` file is configured correctly.

---

## Running the AI Chat

```bash
uv run src/client/main.py src/server/harbor-mcp-server.py
```

Expected output:
```
Connected to server with tools: ['getProjects', 'getRepositories', 'getArtifacts']

MCP Client Started!
Type your queries or 'quit' to exit.

Query:
```

Now just type naturally — no special syntax needed:
```
Query: List all the projects in the registry
Query: Show me the repositories in project demo
Query: What artifact tags are available for my-alpine in project demo?
Query: quit
```

---

## How It All Fits Together — The Full Flow

1. You type a question at the `Query:` prompt.
2. The **MCP Client** sends your question along with the list of available tools to Ollama.
3. **Ollama** figures out which tool to call (e.g. `getRepositories`) and what arguments to pass.
4. The client calls that tool on the **MCP Server** through a local subprocess.
5. The **MCP Server** calls the real Harbor REST API with your credentials from `.env`.
6. The Harbor response travels back up to Ollama, which formats it into a readable answer.
7. You see the answer in your terminal.

---

## Tools available

- Name: getProjects
  Description: Get all projects in the Harbor registry

- Name: getRepositories
  Description: Get all repositories in a Harbor project

- Name: getArtifacts
  Description: Get all artifacts details in a Harbor repository

---

## Troubleshooting

| Problem you see | What to do |
|---|---|
| `Could not connect to Ollama` | Run `ollama serve` or restart: `sudo systemctl restart ollama.service` |
| `Model does not support tools` | Pull a tool-capable model and update `OLLAMA_MODEL` in `src/.env` |
| `401 Unauthorized` from Harbor | Double-check `HARBOR_USERNAME` and `HARBOR_PASSWORD` in `src/.env` |
| `SSL certificate verify failed` | Set `INSECURE_SKIP_TLS_VERIFY=true` in `src/.env` |
| `VIRTUAL_ENV does not match` warning from uv | Harmless. Fix: `deactivate && source .venv/bin/activate` before running |
| Empty results — no projects or repos returned | Make sure your Harbor account has at least **Guest** role on the projects |


