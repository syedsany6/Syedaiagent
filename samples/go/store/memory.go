package store

import (
	"sync"

	"github.com/google/A2A/samples/go/schema"
)

// TaskStore defines the interface for storing and retrieving A2A tasks.
type TaskStore interface {
	Get(id string) (*schema.Task, bool)
	Put(task *schema.Task)
}

// InMemoryTaskStore implements TaskStore using an in-memory map.
type InMemoryTaskStore struct {
	mu    sync.RWMutex
	tasks map[string]*schema.Task
}

// NewInMemoryTaskStore creates a new InMemoryTaskStore.
func NewInMemoryTaskStore() *InMemoryTaskStore {
	return &InMemoryTaskStore{
		tasks: make(map[string]*schema.Task),
	}
}

// Get retrieves a task by its ID.
func (s *InMemoryTaskStore) Get(id string) (*schema.Task, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	task, found := s.tasks[id]
	return task, found
}

// Put stores a task, overwriting if the ID already exists.
func (s *InMemoryTaskStore) Put(task *schema.Task) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.tasks[task.ID] = task
} 