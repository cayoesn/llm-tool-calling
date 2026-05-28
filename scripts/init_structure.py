import os

directories = [
    "app/api", "app/core", "app/runtime", "app/tools", "app/planner",
    "app/execution", "app/validation", "app/observability", "app/security",
    "app/schemas", "app/services", "app/telemetry", "app/config",
    "tests/unit", "tests/integration", "tests/fixtures",
    "docker",
    "monitoring/grafana", "monitoring/loki", "monitoring/promtail",
    "monitoring/prometheus", "monitoring/jaeger",
    "scripts", "docs"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created: {directory}")
