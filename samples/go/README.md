# A2A Protocol Go Sample

This directory contains a Go implementation of the A2A protocol, including:

- Data structures for the A2A protocol
- A simple client implementation
- A server implementation
- Example usage

## Directory Structure

```
.
├── client/     # Client implementation
├── models/     # Data structures
├── server/     # Server implementation
├── examples/   # Example usage
├── go.mod      # Go module definition
└── README.md   # This file
```

## Getting Started

1. Make sure you have Go 1.24.0 or later installed.

2. Navigate to the `samples/go` directory:
   ```bash
   cd samples/go
   ```

3. Run the example:
   ```bash
   go run examples/main.go
   ```

## Implementation Details

### Models

The `models` package contains all the data structures for the A2A protocol, including:

- JSON-RPC base structures
- Agent-related structures (AgentCard, AgentSkill, etc.)
- Task-related structures (Task, TaskStatus, etc.)
- Request and response structures
- Error codes and error handling

### Client

The `client` package provides a simple HTTP client implementation for interacting with A2A agents. It supports:

- Sending tasks
- Getting task status
- Canceling tasks
- Error handling
- JSON-RPC 2.0 compliant requests and responses

### Server

The `server` package provides a JSON-RPC 2.0 compliant server implementation for the A2A protocol. Features include:

- Support for core A2A methods:
  - `tasks/send`: Send a new task
  - `tasks/get`: Get task status
  - `tasks/cancel`: Cancel a task
- Thread-safe task storage
- Task history tracking
- Error handling with A2A error codes
- Customizable task handler interface

### Example

The example in `examples/main.go` demonstrates how to:

1. Create an A2A client
2. Send a task to an agent
3. Poll for task status updates
4. Handle task completion, failure, or cancellation

## Testing

Run the tests for all components:

```bash
go test ./...
```

Each package includes its own test suite:
- Client tests verify request/response handling
- Server tests verify task processing and error handling
- Model tests verify data structure serialization

## Contributing

Feel free to contribute to this implementation by:

1. Adding more features to the client or server
2. Implementing additional A2A protocol methods
3. Adding more examples
4. Improving error handling
5. Adding tests
6. Improving documentation

## License

This implementation is provided under the same license as the A2A protocol specification. 