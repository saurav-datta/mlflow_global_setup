# MLflow Global Setup

Containerized MLflow tracking server with persistent storage.

## Quick Start

```bash
# Build image
sh scripts/build_image.sh

# Stop and Build image
uv run scripts/stop_container.py && sh scripts/build_image.sh

# Start container (port 5500)
uv run scripts/run_container.py

# Configure shell
source mlflow_env.sh
```

UI: http://localhost:5500

## Usage

**Direct logging:**
```bash
uv run scripts/test_mlflow_project.py
```

**Decorator:**
```python
from mlflow_utils import mlflow_track

@mlflow_track(experiment_name="My_Experiment")
def train():
    return {"params": {...}, "metrics": {...}}
```

# Test Decorator
```bash
source mlflow_env.sh && uv run scripts/test_decorator_example.py
OR
source mlflow_env.sh && python scripts/test_decorator_example.py
```

## Commands

```bash
# Stop container
uv run scripts/stop_container.py
OR
python scripts/stop_container.py

# Check port
lsof -i :5500
```

## Config

- MLflow version: `pyproject.toml`
- Port/paths: `mlflow.env`
- Data: `~/mlflow` (default)
