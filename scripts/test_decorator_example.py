import random
from mlflow_utils import mlflow_track, get_server_config


@mlflow_track(experiment_name="Test_Decorator")
def train_model(lr=0.01, epochs=10):
    """Example: Simple model training"""
    accuracy = random.uniform(0.85, 0.99)
    loss = random.uniform(0.01, 0.1)

    return {
        "params": {"learning_rate": lr, "epochs": epochs},
        "metrics": {"accuracy": accuracy, "loss": loss},
    }


if __name__ == "__main__":
    for k, v in get_server_config().items():
        print(f"{k}:{v}")
    train_model(lr=0.001, epochs=20)
    print("Done!")
