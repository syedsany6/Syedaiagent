package main

import (
	"flag"
	"fmt"
	"log/slog"
	"net/http"
	"os"

	"github.com/google/A2A/samples/go/agent"
	"github.com/google/A2A/samples/go/store"
)

func main() {
	port := flag.Int("port", 8080, "Port to listen on")
	flag.Parse()

	// Initialize structured logger (slog)
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil)) // Logs JSON to stdout
	slog.SetDefault(logger)

	addr := fmt.Sprintf(":%d", *port)

	// Initialize dependencies
	taskStore := store.NewInMemoryTaskStore()
	a2aHandler := agent.NewA2AHandler(logger, taskStore)

	// Setup HTTP server
	mux := http.NewServeMux()
	mux.Handle("/a2a", a2aHandler) // Endpoint for A2A requests

	server := &http.Server{
		Addr:    addr,
		Handler: mux,
	}

	logger.Info("Starting A2A Go sample agent", slog.String("address", addr), slog.String("endpoint", "/a2a"))
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		logger.Error("Failed to start server", slog.String("error", err.Error()))
		os.Exit(1)
	}
} 