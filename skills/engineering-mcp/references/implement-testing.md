# Testing and Shipping MCP Servers

Reference for the test pyramid and the build/distribution pipeline for an MCP server. Read it before declaring a server ready to ship.

## Testing

**Unit tests for tool logic (without the MCP layer):**
```rust
#[cfg(test)]
mod tests {
    use super::*;
    #[tokio::test]
    async fn test_add() {
        let server = MyServer::new();
        let result = server.add(Parameters(MyToolParams { a: 2, b: 3 })).await;
        assert_eq!(result, "5");
    }
}
```

**Integration test with the MCP Inspector in CLI mode (the official debug tool, no browser needed):**
```bash
# Build your server
cargo build --release

# Basic usage
npx @modelcontextprotocol/inspector --cli node build/index.js

# With config file
npx @modelcontextprotocol/inspector --cli --config path/to/config.json --server myserver

# List available tools
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list

# Call a specific tool
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/call --tool-name mytool --tool-arg key=value --tool-arg another=value2

# Call a tool with JSON arguments
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/call --tool-name mytool --tool-arg 'options={"format": "json", "max_tokens": 100}'

# List available resources
npx @modelcontextprotocol/inspector --cli node build/index.js --method resources/list

# List available prompts
npx @modelcontextprotocol/inspector --cli node build/index.js --method prompts/list

# Connect to a remote MCP server (default is SSE transport)
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com

# Connect to a remote MCP server (with Streamable HTTP transport)
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com --transport http --method tools/list

# Connect to a remote MCP server (with custom headers)
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com --transport http --method tools/list --header "X-API-Key: your-api-key"

# Call a tool on a remote server
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com --method tools/call --tool-name remotetool --tool-arg param=value

# List resources from a remote server
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com --method resources/list
```

The inspector in `--cli` mode is the ground truth for what your schema actually looks like on the wire. It speaks JSON-RPC over stdio (or HTTP if you set the URL), lists your tools/resources/prompts, lets you call each tool with arbitrary args, and shows every request/response frame on the wire — all without a web browser. **AI agents should default to `--cli` mode**; the interactive web UI is for human inspection only.

**End-to-end test with a real client:**
Use a real MCP host (Claude Code, Cline, Continue) and try the user's actual workflows. This catches tool-selection accuracy problems that unit tests miss.

**Schema validation test:**
```rust
// Use the schemars-generated JSON Schema to validate arbitrary input
let schema = schemars::schema_for!(MyToolParams);
let result = jsonschema::validate(&schema, &json_input);
assert!(result.is_ok());
```

## Building and shipping

```bash
# Build a release binary (always release for stdio servers — debug builds have slow startup)
cargo build --release

# Run locally for manual testing
./target/release/my-mcp-server

# Run with debug logging
RUST_LOG=my_mcp_server=debug,rmcp=info ./target/release/my-mcp-server
```

**Binary size optimization** (rmcp servers can be 4-10 MB):
```toml
# Cargo.toml
[profile.release]
strip = "symbols"
lto = "thin"
codegen-units = 1
opt-level = 3
```

**Cross-compilation for distribution** (for stdio servers you ship to users):
```bash
cargo install cross
cross build --release --target x86_64-unknown-linux-gnu
cross build --release --target x86_64-apple-darwin
cross build --release --target aarch64-apple-darwin
cross build --release --target x86_64-pc-windows-msvc
```
