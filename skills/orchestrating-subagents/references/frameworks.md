# Agent Orchestration Frameworks

Guidelines for implementing multi-agent patterns using popular frameworks.

## LangGraph

**Best for**: Cyclic workflows and complex state management.

- **Nodes and Edges**: Represent agents and their transitions explicitly.
- **State Management**: Use a shared `State` object to pass information between nodes.
- **Cycles**: Ideal for supervisor loops that need to revisit previous steps based on critic feedback.

## AutoGen

**Best for**: Conversational and event-driven patterns.

- **GroupChat**: Agents interact via message-passing in a shared room.
- **Event-Driven**: Agents react to specific keywords or signals in the conversation.
- **Peer-to-Peer**: Naturally supports swarm-like behaviors where agents decide when to speak.

## CrewAI

**Best for**: Role-based process flows.

- **Crews and Tasks**: Define specialized workers with clear assignments.
- **Process Hierarchies**: Supports sequential, hierarchical, and consensual processes.
- **Specialization**: Excellent for production pipelines where tasks flow through a "crew" of specialists.

## LlamaIndex Workflows

**Best for**: Data-centric agentic RAG.

- **Event-Driven**: Optimized for connecting retrieval, synthesis, and evaluation steps.
- **Observability**: Built-in tracking for complex data retrieval flows.

## Implementation Patterns

- **Supervisor/Orchestrator**: Map to a LangGraph supervisor node or a CrewAI manager agent.
- **Peer-to-Peer/Swarm**: Map to AutoGen GroupChat or LangGraph's decentralized edges.
- **Hierarchical**: Map to CrewAI's hierarchical process or nested LangGraph graphs.

## Decision Rule
- Need strict, cyclic state control? → **LangGraph**
- Need dynamic conversational interaction? → **AutoGen**
- Need structured, role-based task execution? → **CrewAI**
- Need event-driven, retrieval-heavy orchestration? → **LlamaIndex Workflows**
