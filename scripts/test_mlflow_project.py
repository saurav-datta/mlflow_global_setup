import mlflow
import os
import tempfile
import shutil
import random


def test_mlflow():
    # Load MLflow tracking URI from env
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5500")
    mlflow.set_tracking_uri(tracking_uri)

    print(f"Using MLflow tracking URI: {tracking_uri}")

    # Create or set an experiment
    experiment_name = "Test_Basic"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        # Log a parameter (e.g., a hyperparameter)
        param_value = random.randint(1, 100)
        mlflow.log_param("sample_param", param_value)

        # Log a metric (e.g., a performance measure)
        metric_value = random.random()
        mlflow.log_metric("sample_metric", metric_value)

        print(f"Logged Param: sample_param={param_value}")
        print(f"Logged Metric: sample_metric={metric_value}")
    print("MLflow test completed successfully.")

if __name__ == "__main__":
    test_mlflow()
