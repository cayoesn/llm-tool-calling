from prometheus_client import Counter, Histogram, Gauge

# Metrics definitions
REQUEST_COUNT = Counter(
    "app_request_count", "Total number of requests", ["method", "endpoint"]
)

TOOL_EXECUTION_COUNT = Counter(
    "tool_execution_count", "Total number of tool executions", ["tool_name", "status"]
)

TOOL_LATENCY = Histogram(
    "tool_latency_seconds", "Latency of tool executions", ["tool_name"]
)

ACTIVE_EXECUTIONS = Gauge(
    "active_tool_executions", "Number of currently running tool executions"
)

TOOL_RETRY_COUNT = Counter(
    "tool_retry_count", "Number of tool retries", ["tool_name"]
)
