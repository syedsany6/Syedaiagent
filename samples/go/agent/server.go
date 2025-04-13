package agent

import (
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"

	"github.com/google/A2A/samples/go/schema"
	"github.com/google/A2A/samples/go/store"
)

// A2AHandler handles A2A protocol requests.
type A2AHandler struct {
	logger *slog.Logger
	store  store.TaskStore
}

// NewA2AHandler creates a new A2AHandler.
func NewA2AHandler(logger *slog.Logger, store store.TaskStore) *A2AHandler {
	return &A2AHandler{
		logger: logger,
		store:  store,
	}
}

// ServeHTTP handles incoming HTTP requests.
func (h *A2AHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		h.logger.Warn("Method not allowed", slog.String("method", r.Method), slog.String("path", r.URL.Path))
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		h.writeJSONRPCError(w, nil, -32700, "Parse error", err.Error())
		return
	}
	defer r.Body.Close()

	var req schema.JSONRPCRequest
	if err := json.Unmarshal(body, &req); err != nil {
		h.writeJSONRPCError(w, nil, -32700, "Parse error", err.Error())
		return
	}

	if req.JSONRPC != "2.0" {
		h.writeJSONRPCError(w, req.ID, -32600, "Invalid Request", "Invalid JSON-RPC version")
		return
	}

	requestLogger := h.logger.With(slog.String("method", req.Method), slog.Any("id", req.ID))
	requestLogger.Info("Received request")

	switch req.Method {
	case "tasks/send":
		h.handleTaskSend(w, req, requestLogger)
	case "tasks/get":
		h.handleTaskGet(w, req, requestLogger)
	default:
		errMsg := fmt.Sprintf("Method '%s' not supported", req.Method)
		requestLogger.Warn("Method not found", slog.String("error", errMsg))
		h.writeJSONRPCError(w, req.ID, -32601, "Method not found", errMsg)
	}
}

// handleTaskSend processes tasks/send requests.
func (h *A2AHandler) handleTaskSend(w http.ResponseWriter, req schema.JSONRPCRequest, logger *slog.Logger) {
	var params schema.TaskSendParams
	if err := json.Unmarshal(req.Params, &params); err != nil {
		logger.Error("Invalid params for tasks/send", slog.String("error", err.Error()))
		h.writeJSONRPCError(w, req.ID, -32602, "Invalid params", err.Error())
		return
	}

	logger = logger.With(slog.String("task_id", params.ID))

	// --- Basic Echo Logic ---
	now := time.Now().UTC().Format(time.RFC3339Nano)
	responseMessage := schema.Message{
		Role:     "agent",
		// IMPORTANT: This is just an echo. A real agent would process the input
		// (params.Message.Parts) and construct meaningful output parts here.
		Parts:    params.Message.Parts, // Echo back the input parts
		Metadata: map[string]interface{}{"echo_response": true},
	}
	task := &schema.Task{
		ID:        params.ID,
		SessionID: params.SessionID,
		Status: schema.TaskStatus{
			State:     schema.TaskStateCompleted, // Immediately complete
			Message:   &responseMessage,
			Timestamp: &now,
		},
		Metadata: params.Metadata, // Echo metadata
	}
	// ------------------------

	h.store.Put(task)
	logger.Info("Task created and completed")

	resp := schema.JSONRPCResponse{
		JSONRPCMessage: schema.JSONRPCMessage{
			JSONRPCMessageIdentifier: schema.JSONRPCMessageIdentifier{ID: req.ID},
			JSONRPC:                  "2.0",
		},
		Result: task, // Return the completed task object
	}
	h.writeJSONResponse(w, resp, logger)
}

// handleTaskGet processes tasks/get requests.
func (h *A2AHandler) handleTaskGet(w http.ResponseWriter, req schema.JSONRPCRequest, logger *slog.Logger) {
	var params schema.TaskQueryParams
	if err := json.Unmarshal(req.Params, &params); err != nil {
		logger.Error("Invalid params for tasks/get", slog.String("error", err.Error()))
		h.writeJSONRPCError(w, req.ID, -32602, "Invalid params", err.Error())
		return
	}

	logger = logger.With(slog.String("task_id", params.ID))

	task, found := h.store.Get(params.ID)
	if !found {
		errMsg := fmt.Sprintf("Task with ID '%s' not found", params.ID)
		logger.Warn("Task not found", slog.String("error", errMsg))
		h.writeJSONRPCError(w, req.ID, -32001, "Task not found", errMsg)
		return
	}

	logger.Info("Retrieved task")

	resp := schema.JSONRPCResponse{
		JSONRPCMessage: schema.JSONRPCMessage{
			JSONRPCMessageIdentifier: schema.JSONRPCMessageIdentifier{ID: req.ID},
			JSONRPC:                  "2.0",
		},
		Result: task, // Return the found task object
	}
	h.writeJSONResponse(w, resp, logger)
}

// writeJSONResponse sends a JSON response.
func (h *A2AHandler) writeJSONResponse(w http.ResponseWriter, resp interface{}, logger *slog.Logger) {
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		logger.Error("Error encoding JSON response", slog.String("error", err.Error()))
		// Attempt to write a minimal error if encoding fails, but might also fail.
		http.Error(w, `{"jsonrpc":"2.0","error":{"code":-32603,"message":"Internal error"},"id":null}`, http.StatusInternalServerError)
	}
}

// writeJSONRPCError sends a JSON-RPC error response.
func (h *A2AHandler) writeJSONRPCError(w http.ResponseWriter, id *interface{}, code int, message string, data interface{}) {
	rpcErr := schema.JSONRPCError{
		Code:    code,
		Message: message,
		Data:    data,
	}
	resp := schema.JSONRPCResponse{
		JSONRPCMessage: schema.JSONRPCMessage{
			JSONRPCMessageIdentifier: schema.JSONRPCMessageIdentifier{ID: id},
			JSONRPC:                  "2.0",
		},
		Error: &rpcErr,
	}

	h.logger.Warn("Sending error response",
		slog.Int("code", code),
		slog.String("message", message),
		slog.Any("data", data),
		slog.Any("id", id),
	)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError) // Often appropriate for RPC errors
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		h.logger.Error("Error encoding JSON-RPC error response", slog.String("error", err.Error()))
	}
}