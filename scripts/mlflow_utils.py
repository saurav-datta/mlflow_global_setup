import mlflow
import os
from functools import wraps


def mlflow_track(experiment_name=None, run_name=None):
    """
    Decorator to track function execution with MLflow.

    Function should return dict with "params" and/or "metrics":
        return {"params": {...}, "metrics": {...}}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5500")
            mlflow.set_tracking_uri(tracking_uri)

            if experiment_name:
                mlflow.set_experiment(experiment_name)

            with mlflow.start_run(run_name=run_name or func.__name__):
                result = func(*args, **kwargs)

                if isinstance(result, dict):
                    if "params" in result:
                        for k, v in result["params"].items():
                            mlflow.log_param(k, v)

                    if "metrics" in result:
                        for k, v in result["metrics"].items():
                            mlflow.log_metric(k, v)

                return result

        return wrapper
    return decorator


def get_server_config():
    results = {}
    results['tracking_uri'] = mlflow.get_tracking_uri()
    results['registry_uri'] = mlflow.get_registry_uri()
    return results
