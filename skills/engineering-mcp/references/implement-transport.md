# Server Lifecycle and Transport

Reference for the MCP server lifecycle and transport choice. Read it before deciding on stdio vs Streamable HTTP, and before implementing initialization or shutdown handling.

## Server lifecycle

```
spawn server process
  ↓
initialize handshake
  → client sends protocolVersion + clientInfo + capabilities
  → server responds with protocolVersion + serverInfo + capabilities
  → client sends "initialized" notification
  ↓
MCP requests flow
  → tools/list
  → tools/call
  → resources/list, resources/read
  → prompts/list, prompts/get
  ↓
shutdown
  → stdio: client closes stdin
  → Streamable HTTP: client closes connection
```

**Initialization in rmcp:**
```rust
let service = server.serve(transport).await?;
// service.waiting() drives the request loop until shutdown
service.waiting().await?;
```

**Handling `notifications/initialized`:**
rmcp handles this for you when you use `serve()`. If you implement the lower-level `serve_with_ct` or build the service by hand, remember that `notifications/initialized` is a notification (no response expected).

**Tool list changes (`notifications/tools/list_changed`):**
If your tool set is dynamic, set `listChanged: true` in your capabilities and emit the notification when the set changes:
```rust
service.notify_tool_list_changed().await?;
```

## Transport choice

**stdio (default for local tools):**
- One process per client
- No network config
- Fastest latency (microseconds)
- Logging must go to stderr (stdout is the protocol)
- The most common pattern for IDEs and CLI wrappers

```rust
use rmcp::transport::stdio;
let transport = stdio();
let service = server.serve(transport).await?;
```

**Streamable HTTP (remote / multi-client):**
- One process serves many clients
- HTTPS + auth in production
- 10-50ms latency (network overhead)
- Origin header validation required (DNS rebinding protection)
- Mcp-Session-Id header for stateful sessions

```rust
use rmcp::transport::streamable_http_server::tower::StreamableHttpService;
use tower::ServiceBuilder;

let service = StreamableHttpService::new(
    || Ok(MyServer::new()),
    Default::default(),
);
let router = axum::Router::new().nest_service("/mcp", service);
// bind to 0.0.0.0:3000 with TLS termination in production
```

**HTTP+SSE (legacy, only for 2024-11-05 clients):**
- Two endpoints: `/sse` (server stream) and `/messages` (client POST)
- Deprecated in 2025-03-26 spec
- New servers should NOT use this; legacy clients may still expect it

**Decision matrix:**

| Need | Use |
|---|---|
| Local CLI / IDE plugin / single-user | **stdio** |
| Hosted SaaS / multi-tenant | **Streamable HTTP** |
| Need to support 2024-11-05 clients | **HTTP+SSE** alongside Streamable HTTP |
| Need both local and remote | Expose both transports via a flag (one binary, two modes) |
