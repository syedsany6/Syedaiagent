# A2A Protocol - Go Sample

This directory contains sample implementations demonstrating the Agent2Agent (A2A) protocol using Go.

## Overview

This sample provides a basic A2A agent implementation, structured into several packages:

- **`schema`**: Go structs representing the A2A JSON-RPC types (`schema/schema.go`).
- **`store`**: An interface (`TaskStore`) and an in-memory implementation (`InMemoryTaskStore`) for managing task state (`store/memory.go`).
- **`agent`**: The main A2A HTTP handler (`A2AHandler`) which uses the `TaskStore` and handles JSON-RPC method dispatch (`agent/server.go`). It uses structured logging (`log/slog`).
- **`main`**: The entry point that initializes logging (`log/slog` with JSON output), the store, and the agent handler, and starts the HTTP server (`main.go`).

## Request Flow Diagram

The following diagram illustrates the typical flow of a request through the sample agent:

```ascii
+---------------------+          +------------------------+          +----------------------+          +---------------------+          +-------------+
| Client (e.g. curl)  |          | HTTP Server (main.go)  |          | A2AHandler (agent)   |          | TaskStore (store)   |          | Logger (slog)|
+---------------------+          +------------------------+          +----------------------+          +---------------------+          +-------------+
         |                               |                                   |                               |                         |
         | POST /a2a (JSON-RPC Req)      |                                   |                               |                         |
         |------------------------------>|                                   |                               |                         |
         |                               | ServeHTTP(req)                    |                               |                         |
         |                               |---------------------------------->|                               |                         |
         |                               |                                   | Log request received          |                         |
         |                               |                                   |-------------------------------------------------------->|
         |                               |                                   | Decode JSON-RPC               |                         |
         |                               |                                   |-----------------------------\|                         |
         |                               |                                   |                             | |                         |
         |                               |                                   | <---- Method Dispatch ------> | |                         |
         |                               |                                   |                             | |                         |
         |                               |                                   |  IF tasks/send:             | |                         |
         |                               |                                   |   Put(task)                 | |                         |
         |                               |                                   |------------------------------>|                         |
         |                               |                                   |                             |<| (ok)                  |
         |                               |                                   |                             |-------------------------|
         |                               |                                   |   Log task created/completed|                         |
         |                               |                                   |-------------------------------------------------------->|
         |                               |                                   |  ELSE IF tasks/get:         | |                         |
         |                               |                                   |   Get(taskID)               | |                         |
         |                               |                                   |------------------------------>|                         |
         |                               |                                   |                             |<| task                  |
         |                               |                                   |                             |-------------------------|
         |                               |                                   |   Log task retrieved        |                         |
         |                               |                                   |-------------------------------------------------------->|
         |                               |                                   |                             | |                         |
         |                               |                                   | Encode JSON-RPC Response    | |                         |
         |                               |                                   |<-----------------------------/ |                         |
         |                               | response                          |                               |                         |
         |                               |<----------------------------------|                               |                         |
         | HTTP Response (JSON-RPC Resp) |                                   |                               |                         |
         |<------------------------------|                                   |                               |                         |
         |                               |                                   |                               |                         |

```

## Running the Sample

Follow these steps to run the agent and interact with it:

1.  **Start the Server**:

    - Navigate to the Go sample directory in your terminal:
      ```bash
      cd samples/go
      ```
    - Run the server:
      ```bash
      go run main.go
      ```
    - The server will start listening on port 8080 (by default) and output its first structured log message (using `slog` JSON handler):
      ```json
      {
        "time": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
        "level": "INFO",
        "msg": "Starting A2A Go sample agent",
        "address": ":8080",
        "endpoint": "/a2a"
      }
      ```
      _(Timestamp will vary)_.

2.  **Send a Task (`tasks/send`)**:

    - Open **another terminal window**.
    - Use `curl` to send a POST request with a `tasks/send` JSON-RPC message:
      ```bash
      curl -X POST http://localhost:8080/a2a \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
          "id": "task-123",
          "message": {
            "role": "user",
            "parts": [
              {
                "text": "Hello agent!"
              }
            ]
          }
        },
        "id": 1
      }'
      ```
    - **Server Logs:** In the _first_ terminal (where the server is running), you will see structured logs related to this request:
      ```json
      {"time":"YYYY-MM-DDTHH:MM:SS.ffffffZ","level":"INFO","msg":"Received request","method":"tasks/send","id":1}
      {"time":"YYYY-MM-DDTHH:MM:SS.ffffffZ","level":"INFO","msg":"Task created and completed","method":"tasks/send","id":1,"task_id":"task-123"}
      ```
    - **Curl Output:** In the _second_ terminal (where you ran `curl`), you will receive the JSON-RPC response:
      ```json
      {
        "id": 1,
        "jsonrpc": "2.0",
        "result": {
          "id": "task-123",
          "sessionId": null,
          "status": {
            "state": "completed",
            "message": {
              "role": "agent",
              "parts": [
                {
                  "Type": "text",
                  "Text": "Hello agent!",
                  "Metadata": null
                }
              ],
              "metadata": {
                "echo_response": true
              }
            },
            "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
          },
          "artifacts": null,
          "metadata": null
        }
      }
      ```
      _(Note: Timestamps and exact formatting might vary slightly. Go's default JSON marshaler might add fields like `Type` even if omitted in the struct definition if they aren't explicitly tagged with `omitempty` and have a zero value like `nil` or `""`.)_

3.  **Get Task Status (`tasks/get`)**:
    - In the _second_ terminal, use `curl` again to send a `tasks/get` request for the task you just created:
      ```bash
      curl -X POST http://localhost:8080/a2a \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "tasks/get",
        "params": {
          "id": "task-123"
        },
        "id": 2
      }'
      ```
    - **Server Logs:** The server terminal will show logs for this request:
      ```json
      {"time":"YYYY-MM-DDTHH:MM:SS.ffffffZ","level":"INFO","msg":"Received request","method":"tasks/get","id":2}
      {"time":"YYYY-MM-DDTHH:MM:SS.ffffffZ","level":"INFO","msg":"Retrieved task","method":"tasks/get","id":2,"task_id":"task-123"}
      ```
    - **Curl Output:** The `curl` command will output the same task details retrieved from the agent's store:
      ```json
      {
        "id": 2, // Note the response ID matches the request ID
        "jsonrpc": "2.0",
        "result": {
          "id": "task-123"
          // ... rest of the task details as shown in the previous step ...
        }
      }
      ```

## Further Development

This sample provides a foundation. Potential extensions include:

- Implementing more A2A methods (e.g., `tasks/cancel`, streaming with `tasks/sendSubscribe`).
- Adding more sophisticated agent logic beyond a simple echo.
- Implementing error handling for different scenarios (e.g., invalid part types).
- Swapping the `InMemoryTaskStore` with a persistent storage implementation.
- Creating an A2A client implementation in Go.
- Integrating with specific Go agent frameworks or libraries.
