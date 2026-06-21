# Building an MCP Client with the rmcp SDK

This reference is for **agents that need to act as an MCP client** — typically a custom orchestration layer (Rust service, agent runtime, or test harness) that spawns an MCP server subprocess or connects to a remote Streamable HTTP server, then calls its tools directly. If you're inside Claude Code and just want the host to handle the JSON-RPC, you don't need this — see `references/client-usage.md` instead.

## §1. The `client` feature flag

The rmcp crate exposes client types behind a feature flag. Add it to your `Cargo.toml`:

```toml
[dependencies]
rmcp = { version = "0.3", features = ["client", "transport-io", "schemars"] }
tokio = { version = "1", features = ["full"] }
```

**Required features for client use:**
- `client` — client-side types and the `ClientHandler` trait
- `transport-io` — stdio client (spawn server subprocess, speak JSON-RPC)
- `transport-streamable-http-client` — Streamable HTTP client (connect to remote servers)
- `schemars` — re-export of `schemars` for tool input/output types

## §2. The `ClientHandler` trait

Just as the server side implements `ServerHandler`, the client side implements `ClientHandler` to react to server-initiated requests (sampling, elicitation, roots):

```rust
use rmcp::{
    ClientHandler, ServiceExt,
    model::*,
    transport::stdio,
};

#[derive(Clone)]
pub struct MyClient;

impl ClientHandler for MyClient {
    // Called when the server sends a sampling request (server wants the host to run an LLM call)
    // For agents that don't support sampling, return an error:
    // fn create_message(...) -> Result<...> { Err(...) }
    // For agents that DO support it, dispatch to your LLM provider.
    //
    // Other hooks: on_elicitation, on_roots_list_changed
}
```

Most agents don't need to implement all hooks — the defaults return "not supported" errors, which the server should handle gracefully.

## §3. Stdio client (spawn a server subprocess)

The stdio client speaks JSON-RPC over the subprocess's stdin/stdout:

```rust
use rmcp::{ClientHandler, ServiceExt, transport::stdio};
use tokio::process::Command;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Spawn the server subprocess
    let mut cmd = Command::new("./bin/my-mcp-server");
    cmd.stdin(std::process::Stdio::piped());
    cmd.stdout(std::process::Stdio::piped());
    cmd.stderr(std::process::Stdio::piped());

    // Connect via stdio transport
    let transport = stdio::with_command(cmd);
    let service = MyClient.serve(transport).await?;

    // Get the server's tool list
    let tools = service.peer().list_tools(Default::default()).await?;
    for tool in &tools.tools {
        println!("{}: {}", tool.name, tool.description.as_deref().unwrap_or(""));
    }

    // Call a tool
    let result = service
        .peer()
        .call_tool(
            CallToolRequestParam {
                name: "my_tool".into(),
                arguments: Some(serde_json::json!({ "key": "value" }).as_object().unwrap().clone()),
            },
            None,
        )
        .await?;

    // Inspect the result
    if result.is_error.unwrap_or(false) {
        eprintln!("Tool returned an error: {:?}", result.content);
    } else {
        for content in &result.content {
            if let Some(text) = content.as_text() {
                println!("{}", text.text);
            }
        }
    }

    // Shutdown
    service.cancel().await?;
    Ok(())
}
```

**Stderr handling:** the server may write logs to stderr. Capture them for debugging, but don't redirect stderr to stdout (that would corrupt the parent's JSON-RPC stream if you're nested).

## §4. Streamable HTTP client (connect to a remote server)

```rust
use rmcp::transport::streamable_http_client::{StreamableHttpClientTransport, StreamableHttpClientWorker};
use rmcp::{ClientHandler, ServiceExt};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let url = "https://my-mcp-server.example.com/mcp";

    // Build the transport
    let transport = StreamableHttpClientTransport::from_uri(url);

    // Optional: add custom headers (e.g., API key)
    let transport = transport.with_header("X-API-Key", std::env::var("API_KEY")?);

    // Connect
    let service = MyClient.serve(transport).await?;

    // ...same as stdio: list_tools, call_tool, etc.
    Ok(())
}
```

**TLS:** the client uses the system trust store by default. For self-signed certs in dev, configure the transport's TLS builder.

**Auth:** Streamable HTTP clients can send custom headers. For OAuth flows, see the MCP spec's auth section — rmcp provides hook points but doesn't implement the full OAuth dance out of the box.

## §5. Handling `CallToolResult`

The result is a `CallToolResult` with `content: Vec<Content>` and `is_error: Option<bool>`:

```rust
let result = service.peer().call_tool(...).await?;

// Check if the tool itself returned an error
if result.is_error.unwrap_or(false) {
    // The tool completed but wants to report a domain failure
    // (e.g., "file not found")
    // The agent should handle this as a user-facing error
} else {
    // Success — extract the content
    for item in &result.content {
        match item {
            Content::Text(text) => {
                let parsed: serde_json::Value = serde_json::from_str(&text.text)?;
                // Handle parsed JSON
            }
            Content::Image(img) => {
                // img.data is base64-encoded; img.mime_type tells you the format
            }
            Content::Resource(_resource) => {
                // Embedded resource (rare for tool output)
            }
            _ => {}
        }
    }
}
```

**Distinguish three failure modes:**

| Source | Signal | What to do |
|---|---|---|
| Transport error (`Result::Err`) | Call didn't even run | Maybe retry, log, or escalate |
| `is_error: true` | Tool completed, domain failure | Show to user / handle as domain error |
| `Ok` with `is_error: None` or `Some(false)` | Success | Use the content |

## §6. Anti-patterns (client side)

❌ **Spawning the server with `std::process::Command` and reading stdout manually** — use `transport::stdio` so rmcp handles the JSON-RPC framing. Manual framing is a bug factory.
❌ **Forgetting to consume the server's stderr** — server crashes silently show up nowhere if you don't capture stderr.
❌ **Re-sending on transport error without inspecting** — non-idempotent tools (`git_commit`, `db_update`) will double-charge. Inspect the error first; re-send only if it's clearly transient.
❌ **Trying to use the server as a long-lived connection with implicit state** — the MCP spec is stateless. Use explicit handles.
❌ **Building the server's tool list once at startup and caching it forever** — servers can change tool sets (with `listChanged: true`). Re-fetch on `notifications/tools/list_changed` or poll periodically.
