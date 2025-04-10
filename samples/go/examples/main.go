package main

import (
	"fmt"
	"log"
	"time"

	"a2a/client"
	"a2a/models"
)

func main() {
	// Create a new A2A client
	a2aClient := client.NewClient("http://localhost:8080")

	// Create a task message
	message := models.Message{
		Role: "user",
		Parts: []models.Part{
			{
				Type: stringPtr("text"),
				Text: stringPtr("Hello, A2A agent!"),
			},
		},
	}

	// Send a task
	response, err := a2aClient.SendTask(models.TaskSendParams{
		ID:      "task-1",
		Message: message,
	})
	if err != nil {
		log.Fatalf("Failed to send task: %v", err)
	}

	task, ok := response.Result.(*models.Task)
	if !ok {
		log.Fatalf("Expected result to be a Task")
	}

	fmt.Printf("Task sent successfully. Task ID: %s\n", task.ID)

	// Poll for task status
	for {
		response, err := a2aClient.GetTask(models.TaskQueryParams{
			TaskIDParams: models.TaskIDParams{
				ID: task.ID,
			},
		})
		if err != nil {
			log.Fatalf("Failed to get task status: %v", err)
		}

		task, ok = response.Result.(*models.Task)
		if !ok {
			log.Fatalf("Expected result to be a Task")
		}

		fmt.Printf("Task status: %s\n", task.Status.State)

		if task.Status.State == models.TaskStateCompleted ||
			task.Status.State == models.TaskStateFailed ||
			task.Status.State == models.TaskStateCanceled {
			break
		}

		time.Sleep(1 * time.Second)
	}
}

func stringPtr(s string) *string {
	return &s
}
