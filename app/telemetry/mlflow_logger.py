import mlflow
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MLflowLogger:
    def __init__(self):
        self.enabled = False
        try:
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            mlflow.set_experiment(settings.PROJECT_NAME)
            self.enabled = True
            logger.info("MLflow logging initialized successfully.")
        except Exception as e:
            logger.warning(f"MLflow initialization failed: {str(e)}. MLflow logging will be disabled.")

    def log_execution(self, prompt: str, tool_calls: list, results: list, final_response: str):
        if not self.enabled:
            return

        try:
            with mlflow.start_run():
                mlflow.log_param("prompt", prompt)
                mlflow.log_dict({"tool_calls": tool_calls}, "tool_calls.json")
                mlflow.log_dict({"results": results}, "results.json")
                mlflow.log_text(final_response, "final_response.txt")
                
                # Log metrics
                total_latency = sum([r['execution_time'] for r in results])
                mlflow.log_metric("total_tool_latency", total_latency)
                mlflow.log_metric("tool_call_count", len(tool_calls))
                
                success_count = sum([1 for r in results if r['status'] == 'success'])
                mlflow.log_metric("success_rate", success_count / len(results) if results else 1.0)
        except Exception as e:
            logger.error(f"Failed to log to MLflow: {str(e)}")

mlflow_logger = MLflowLogger()
