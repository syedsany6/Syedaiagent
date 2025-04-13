package schema

import "encoding/json"

// TaskState represents the state of a task.
// Corresponds to the TaskState enum in the A2A schema.
type TaskState string

const (
	TaskStateSubmitted     TaskState = "submitted"
	TaskStateWorking       TaskState = "working"
	TaskStateInputRequired TaskState = "input-required"
	TaskStateCompleted     TaskState = "completed"
	TaskStateCanceled      TaskState = "canceled"
	TaskStateFailed        TaskState = "failed"
	TaskStateUnknown       TaskState = "unknown"
)

// JSONRPCMessageIdentifier represents the base ID structure for JSON-RPC messages.
type JSONRPCMessageIdentifier struct {
	ID *interface{} `json:"id,omitempty"` // Can be string, number, or null
}

// JSONRPCMessage represents the base structure for all JSON-RPC messages.
type JSONRPCMessage struct {
	JSONRPCMessageIdentifier
	JSONRPC string `json:"jsonrpc"` // Should always be "2.0"
}

// JSONRPCRequest represents a JSON-RPC request.
type JSONRPCRequest struct {
	JSONRPCMessage
	Method string           `json:"method"`
	Params json.RawMessage `json:"params,omitempty"` // Use RawMessage to delay parsing
}

// JSONRPCError represents a JSON-RPC error object.
type JSONRPCError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// JSONRPCResponse represents a JSON-RPC response.
type JSONRPCResponse struct {
	JSONRPCMessage
	Result interface{}   `json:"result,omitempty"`
	Error  *JSONRPCError `json:"error,omitempty"`
}

// --- Core A2A Data Structures ---

// AgentAuthentication defines authentication schemes.
type AgentAuthentication struct {
	Schemes     []string `json:"schemes"`
	Credentials *string  `json:"credentials,omitempty"`
}

// AgentCapabilities describes agent capabilities.
type AgentCapabilities struct {
	Streaming              *bool `json:"streaming,omitempty"`
	PushNotifications      *bool `json:"pushNotifications,omitempty"`
	StateTransitionHistory *bool `json:"stateTransitionHistory,omitempty"`
}

// AgentProvider represents the agent provider.
type AgentProvider struct {
	Organization string  `json:"organization"`
	URL          *string `json:"url,omitempty"`
}

// AgentSkill defines a specific skill.
type AgentSkill struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description *string   `json:"description,omitempty"`
	Tags        []string  `json:"tags,omitempty"`
	Examples    []string  `json:"examples,omitempty"`
	InputModes  []string  `json:"inputModes,omitempty"`
	OutputModes []string  `json:"outputModes,omitempty"`
}

// AgentCard represents the metadata card for an agent.
type AgentCard struct {
	Name               string               `json:"name"`
	Description        *string              `json:"description,omitempty"`
	URL                string               `json:"url"`
	Provider           *AgentProvider       `json:"provider,omitempty"`
	Version            string               `json:"version"`
	DocumentationURL   *string              `json:"documentationUrl,omitempty"`
	Capabilities       AgentCapabilities    `json:"capabilities"`
	Authentication     *AgentAuthentication `json:"authentication,omitempty"`
	DefaultInputModes  []string             `json:"defaultInputModes,omitempty"`
	DefaultOutputModes []string             `json:"defaultOutputModes,omitempty"`
	Skills             []AgentSkill         `json:"skills"`
}

// FileContentBase represents the base for file content.
type FileContentBase struct {
	Name     *string `json:"name,omitempty"`
	MimeType *string `json:"mimeType,omitempty"`
}

// FileContentBytes represents file content as base64 bytes.
type FileContentBytes struct {
	FileContentBase
	Bytes string `json:"bytes"` // Required
	URI   string `json:"uri,omitempty"` // Should be omitted if bytes is present
}

// FileContentUri represents file content as a URI.
type FileContentUri struct {
	FileContentBase
	Bytes string `json:"bytes,omitempty"` // Should be omitted if uri is present
	URI   string `json:"uri"` // Required
}

// FileContent represents file content (either bytes or URI).
// Using interface{} because the JSON can be either FileContentBytes or FileContentUri.
// A consuming agent would use a type switch or type assertion to handle the specific type.
type FileContent interface{}

// TextPart represents a text part of a message.
type TextPart struct {
	Type     string                 `json:"type,omitempty"` // Should be "text"
	Text     string                 `json:"text"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// FilePart represents a file part of a message.
type FilePart struct {
	Type     string                 `json:"type,omitempty"` // Should be "file"
	File     FileContent            `json:"file"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// DataPart represents a structured data part of a message.
type DataPart struct {
	Type     string                 `json:"type,omitempty"` // Should be "data"
	Data     map[string]interface{} `json:"data"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// Part represents any part of a message (text, file, data).
// Using interface{} because the JSON can be TextPart, FilePart, or DataPart.
// A consuming agent would use a type switch or type assertion to determine the actual
// type of the part and access its specific fields (e.g., part.(TextPart).Text).
type Part interface{}

// Artifact represents an artifact generated or used by a task.
type Artifact struct {
	Name        *string                `json:"name,omitempty"`
	Description *string                `json:"description,omitempty"`
	Parts       []Part                 `json:"parts"`
	Index       *int                   `json:"index,omitempty"`
	Append      *bool                  `json:"append,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	LastChunk   *bool                  `json:"lastChunk,omitempty"`
}

// Message represents a message exchanged between user and agent.
type Message struct {
	Role     string                 `json:"role"` // "user" or "agent"
	Parts    []Part                 `json:"parts"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// TaskStatus represents the status of a task.
type TaskStatus struct {
	State     TaskState `json:"state"`
	Message   *Message  `json:"message,omitempty"`
	Timestamp *string   `json:"timestamp,omitempty"` // ISO 8601 format
}

// Task represents a task being processed.
type Task struct {
	ID        string                 `json:"id"`
	SessionID *string                `json:"sessionId,omitempty"`
	Status    TaskStatus             `json:"status"`
	Artifacts []Artifact             `json:"artifacts,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// TaskHistory represents the message history of a task.
type TaskHistory struct {
	MessageHistory []Message `json:"messageHistory,omitempty"`
}

// PushNotificationConfig defines push notification settings.
type PushNotificationConfig struct {
	URL            string                `json:"url"`
	Token          *string               `json:"token,omitempty"`
	Authentication *AgentAuthentication `json:"authentication,omitempty"` // Reusing AgentAuthentication for simplicity
}

// --- Request Parameter Types ---

// TaskSendParams are parameters for the tasks/send method.
type TaskSendParams struct {
	ID             string                  `json:"id"`
	SessionID      *string                 `json:"sessionId,omitempty"`
	Message        Message                 `json:"message"`
	PushNotification *PushNotificationConfig `json:"pushNotification,omitempty"`
	HistoryLength  *int                    `json:"historyLength,omitempty"`
	Metadata       map[string]interface{}  `json:"metadata,omitempty"`
}

// TaskIdParams are parameters used for operations needing only a task ID.
type TaskIdParams struct {
	ID       string                 `json:"id"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// TaskQueryParams are parameters for querying task info by ID.
type TaskQueryParams struct {
	TaskIdParams
	HistoryLength *int `json:"historyLength,omitempty"`
}

// TaskPushNotificationConfig includes task ID and push config.
type TaskPushNotificationConfig struct {
	ID                   string                 `json:"id"`
	PushNotificationConfig PushNotificationConfig `json:"pushNotificationConfig"`
} 