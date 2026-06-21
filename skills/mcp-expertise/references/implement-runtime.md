# Runtime Contracts: Logging, Error Mapping, Output Construction

Reference for the three runtime contracts an MCP server must honor: stderr-only logging, error mapping to `rmcp::ErrorData`, and output construction via `CallToolResult`. Read it before implementing any tool that writes logs, surfaces errors, or returns structured output.

## Stderr-only logging

**Critical rule for stdio servers:** anything written to stdout corrupts the JSON-RPC stream and the client disconnects. ALL logs go to stderr.

```rust
use tracing_subscriber::{fmt, prelude::*, EnvFilter};
use tracing;

tracing_subscriber::fmt()
    .with_writer(std::io::stderr)  // ← critical
    .with_env_filter(
        EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| EnvFilter::new("info"))
    )
    .init();

// Usage
tracing::info!("server starting on stdio");
tracing::debug!("got request: {:?}", request);
tracing::error!(?error, "tool call failed");
```

For Streamable HTTP servers, stdout logging is fine (it's not a protocol channel). But stay consistent — use stderr for everything, no matter the transport.

**Common bug:** `println!("debugging: {:?}", state)` in a stdio server. The client silently disconnects. Always use `tracing` or `eprintln!`.

## Error mapping

The error type is `rmcp::ErrorData` (re-exported at the crate root in 0.3).
The 2-arg constructor shape is `(message: impl Into<String>, data: Option<impl Serialize>)`.

```rust
use rmcp::ErrorData;

// Wrap a domain error so it surfaces as a JSON-RPC error response
fn map_domain_error(e: anyhow::Error) -> ErrorData {
    ErrorData::internal_error(
        e.to_string(),                       // human-readable message
        Some(serde_json::json!({ "source": "tool_execution" })),  // optional structured data
    )
}

// In a tool method
#[tool(description = "Read a file")]
async fn read_file(
    &self,
    Parameters(p): Parameters<ReadFileParams>,
) -> Result<rmcp::model::CallToolResult, ErrorData> {
    // Security: validate path
    if !is_path_allowed(&p.path) {
        return Err(ErrorData::invalid_request(
            "access denied: path outside allowed directories",
            None,
        ));
    }
    let content = tokio::fs::read_to_string(&p.path)
        .await
        .map_err(|e| ErrorData::invalid_params(format!("read failed: {e}"), None))?;
    Ok(rmcp::model::CallToolResult::success(vec![
        rmcp::model::Content::text(content)
    ]))
}
```

**`rmcp::ErrorData` constructors (2-arg form, all take `impl Into<String>` + `Option<impl Serialize>`):**
- `ErrorData::parse_error(msg, data)` → JSON-RPC `-32700` (malformed JSON)
- `ErrorData::invalid_request(msg, data)` → JSON-RPC `-32600`
- `ErrorData::method_not_found(msg, data)` → JSON-RPC `-32601`
- `ErrorData::invalid_params(msg, data)` → JSON-RPC `-32602` (most common for schema/validation failures)
- `ErrorData::internal_error(msg, data)` → JSON-RPC `-32603` (use sparingly — true internal bugs only)
- `ErrorData::custom(code, msg, data)` → arbitrary code (use for domain-specific `-32001`…`-32099` codes)
- `ErrorData::resource_not_found(msg, data)` → MCP-specific code for missing resources

**Map your domain error categories to error codes:**
- Validation failed (bad input shape, missing required field) → `-32602` (invalid params)
- Auth failed → custom `-32001`
- Rate limited → custom `-32002`
- Dependency unavailable (downstream service down) → custom `-32003`
- Internal bug (you hit an `unwrap`/panic-recovered branch) → `-32603` (with a clear message — you'll debug from this)

> **Don't conflate tool-returned `is_error: true` with transport errors.** A tool that
> completed and wants to tell the client "the file you asked for doesn't exist"
> should return `Ok(CallToolResult { is_error: Some(true), content: ... })`, NOT
> `Err(...)`. Transport-level `Err(ErrorData)` means the call didn't even run.
> Save `Err` for cases the client should retry, route differently, or escalate.

## Output construction

```rust
use rmcp::model::{CallToolResult, Content};

// Simple text output
Ok(CallToolResult::success(vec![Content::text("the result")]))

// JSON-serialized output
let data = serde_json::json!({ "status": "ok", "count": 42 });
Ok(CallToolResult::success(vec![Content::text(data.to_string())]))

// Multiple content items (text + image)
Ok(CallToolResult::success(vec![
    Content::text(format!("Weather in {city}: {temp}°C, {condition}")),
    Content::image(encoded_image_bytes, "image/png"),
]))

// Error output
Err(rmcp::ErrorData::invalid_request("file not found", Some(json!({ "path": path }))))
```

**For long output**, truncate and return a handle:
```rust
const MAX_INLINE: usize = 50_000;
if content.len() > MAX_INLINE {
    let handle = self.store_blob(content).await;
    Ok(CallToolResult::success(vec![Content::text(format!(
        "[truncated, full output at resource://blobs/{handle}]"
    ))]))
} else {
    Ok(CallToolResult::success(vec![Content::text(content)]))
}
```
