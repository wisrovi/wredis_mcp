# 🔥 wredis-mcp

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/wisrovi/wredis_mcp)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0-orange.svg)](https://modelcontextprotocol.io)

**Transform your AI Agents into expert WRedis Architects.**

`wredis-mcp` is a professional Model Context Protocol (MCP) server that bridges the gap between AI Agents (Claude, Gemini, OpenCode) and **WRedis**. It empowers agents to search, design, and deploy high-performance Redis-backed services following strict industry-standard patterns.

---

## ✨ Key Features

- **🔍 Expert Pattern Catalog**: Query production-ready patterns across all WRedis data structures (Hash, Queue, Stream, Pub/Sub, SortedSet, Geo, Bitmap, HyperLogLog, Pipeline, Transaction, Cache, HA).
- **🏗️ Strict Architecture Enforcement**: Guides AI to output clean code using mandatory `config/`, `cache/`, `repositories/`, and `main.py` folder structures.
- **📘 Architect's Manual**: Built-in expertise for Monolith-to-Redis refactoring, TTL management, key naming, and atomicity patterns.
- **💻 Unified CLI**: Manage your MCP service with simple commands: `run`, `start`, `stop`, and `config`.
- **🛡️ Privacy First**: 100% local execution via `stdio` or `SSE`.

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and run the automated installer, or install via pip:
```bash
pip install -e .
```

### 2. Integration
Get your agent-specific configuration block and installation commands by running:
```bash
wredis-mcp config
```
The CLI will dynamically detect your Python environment and provide exact copy-paste commands for Gemini CLI (e.g. `gemini mcp add ...`) and JSON blocks for Claude Desktop.

---

## 🛠️ CLI Usage

| Command | Description |
| :--- | :--- |
| `wredis-mcp run` | Start the server in `stdio` mode (default for agents). |
| `wredis-mcp start` | Start as an SSE server in the background. |
| `wredis-mcp stop` | Stop the background server. |
| `wredis-mcp config` | Generate and save JSON config to `.agents/wredis-mcp.json`. |
| `wredis-mcp config --print` | Show JSON configuration in stdout (no file creation). |
| `wredis-mcp help` | Show available tools and commands. |

---

## 🛠️ MCP Tools

| Tool | Description |
| :--- | :--- |
| `get_wredis_architect_blueprints` | Copy-pasteable expert code for caching, queues, streams, sessions and atomic transactions. |
| `search_wredis_pattern` | Search the official/community catalog for production-ready Redis patterns. |
| `deploy_wredis_scaffolding` | Deploy a professional WRedis project structure (`config/`, `cache/`, `repositories/`, `main.py`). |
| `get_wredis_architect_manual` | Expert manual for building high-performance Redis-backed systems. |

---

## 📂 Project Structure
- `src/wredis_mcp/`: Core server logic and tools.
- `src/wredis_mcp/catalog.py`: Pattern catalog synchronization with local fallbacks.
- `src/wredis_mcp/templates.py`: Professional boilerplate definitions.
- `examples/`: Sample implementations and use cases.

---

## 📄 License
MIT License - Crafted with ❤️ by **William Rodriguez** (wisrovi).
