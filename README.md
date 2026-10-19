# Multi-Node Remote Management System

A lightweight, centralized tool designed to manage and orchestrate multiple remote machines from a single host over a secure local area network (LAN). It provides seamless switching between active client sessions, non-interactive remote command execution, and direct file/directory transfers without the overhead of maintaining dozens of separate SSH terminal windows.

---

> ### ⚠️ Security Warning & Disclaimer
> **Traffic is sent in plain text: connections are currently NOT encrypted.**
> 
> * **Do not** transmit sensitive data or credentials over untrusted networks or the public internet.
> * This project was developed strictly for personal utility, administrative automation, and educational purposes. It is **not** intended for unauthorized access or any illegal activities.
> * For production environments or public networks, strongly consider industry-standard tools such as `ssh` for remote access and `scp`/`sftp` for secure file transfers.

---

## Architecture & How It Works

The tool relies on a **reverse TCP connection** model:

1. **Control Server:** Runs on the host machine via `ListenServer(connections, host, port)`. It listens for incoming connections and manages multiple concurrent client sessions without arbitrary limits.
2. **Client Agents:** Run in the background on target machines. Upon startup, each client initiates a reverse connection back to the server.
3. **Session Switching:** The operator can seamlessly switch between any connected target nodes, run shell commands, and transfer files/directories in real time.
4. **Fault Tolerance & Reconnection:**
   * If a target machine disconnects abruptly, the server catches the network exception and removes the node from the active connection pool.
   * If the central server drops or restarts, client agents automatically attempt to reconnect at a configurable interval (`TIMEOUT` in `client/main.py`).

---

## Features

* **Centralized Multiplexing:** Control multiple remote endpoints from a single terminal interface.
* **Instant Session Switching:** Switch between connected nodes on the fly.
* **Command Execution:** Run remote CLI commands and receive standard output/error streams.
* **File & Directory Transfers:** Upload and download files or entire directory trees between the host and remote nodes.
* **Automatic Reconnects:** Resilient client agents that continuously retry failed server connections.
* **Built-in Help:** Run with `-h` or `--help` to view available commands and arguments.

---

## Known Limitations

* **No Interactive TTY/PTY Support:** 
  The current implementation does not support interactive programs or REPL environments that require continuous terminal input/output (e.g., `vim`, `nvim`, `nano`, `python`, `node`, `htop`). Running interactive commands will cause the connection to hang while waiting for unbuffered input. If this occurs, restart the server process.

---

## Network Configuration

By default, the client establishes a reverse socket connection to the specified `host:port`.

* **Local Network (LAN):** Provide the internal IP address of the host running `ListenServer`.
* **Remote / Internet Usage:** Point the client to your server's public IP, a Virtual Private Server (VPS), or a tunneling service (e.g., `ngrok`).  
  *(Reminder: Plaintext communication—use tunneling with TLS/VPN if testing over the public internet).*

---

## Planned Roadmap & Improvements

1. **Transport Layer Security & Encryption:**
   * Implement end-to-end encryption for all payload packets.
   * Introduce a secure public-key handshake (e.g., RSA key exchange) upon connection, followed by symmetric session encryption (AES-GCM/ChaCha20) for commands, responses, and file transfers.
   * Maintain a per-client key registry within the `Connections` manager.
2. **Architecture & Modular Refactoring:**
   * Move low-level packet construction routines (`_create_packet`, `_send_packet`) from `execute.py` into `handle_files.py` or a dedicated networking utility module.
   * Decouple command parsing in `command.py` and delegate runtime operations to `execute.py`.
3. **Async I/O Migration:**
   * Transition connection handling from multi-threading to Python's `asyncio` for improved concurrency and lower resource overhead.
4. **Interactive Shell / Pseudo-Terminal (PTY):**
   * Implement PTY forwarding (e.g., via `pty`/`termios`) on the client side to allow interactive CLI applications (`vim`, REPLs) without blocking.
5. **Connection & Session Management:**
   * Add a graceful shutdown broadcast to notify connected clients before server termination.
   * Add client-side socket restart routines triggered via remote commands.
   * Add a `remove_client` command with blacklisting capabilities to prevent unwanted automatic reconnects.
6. **Robust Error Handling:**
   * Implement granular exception classes instead of passing raw stringified error messages.
7. **CLI & Developer Experience:**
   * Build a dedicated CLI interface for both client and server binaries.
   * Refactor and polish the interactive terminal UI/UX.
   * Enforce linting and strict type checks using `ruff` and `mypy`.
   * Introduce a comprehensive unit and integration test suite (`pytest`).
