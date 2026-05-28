# Architecture Documentation

## Core Components

### 1. Tool Registry (`app/runtime/registry.py`)
Centralized management of all available tools. Each tool is registered with its metadata, including name, description, and input/output schemas.

### 2. LLM Planner (`app/planner/planner.py`)
Interfaces with local Ollama (`llama3`) to decide which tools are needed based on the user's prompt. It enforces JSON output for structured tool calls.

### 3. Execution Engine (`app/execution/engine.py`)
Handles the actual execution of tools.
- **Retries**: Configurable retry policies with exponential backoff.
- **Timeouts**: Asyncio-based timeout handling.
- **Validation**: Uses Pydantic v2 to validate inputs and outputs.
- **Security**: Integration with Security Manager for permissions.

### 4. Tool Router (`app/execution/router.py`)
Dispatches tool calls to the execution engine. Supports both parallel and sequential execution.

### 5. Execution Pipeline (`app/execution/pipeline.py`)
The orchestrator that ties everything together:
1. Receives prompt.
2. Calls Planner.
3. Dispatches tool calls via Router.
4. Collects results.
5. Injects results into final context for LLM response.
6. Logs metadata to MLflow.

## Observability Stack

### Distributed Tracing
Uses OpenTelemetry and Jaeger to trace the lifecycle of a request, from API entry to tool execution.

### Metrics
Prometheus collects metrics such as request counts, tool latencies, and retry rates.

### Logging
Structured JSON logging sent to Loki and visualized in Grafana.

### Execution Tracking
MLflow stores every execution's prompt, tool calls, and results for auditing and improvement.
