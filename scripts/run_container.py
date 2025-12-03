import docker
import os
import socket
from dotenv import load_dotenv

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def validate_path(path: str) -> bool:
    """Validate that the path exists, is a directory, and is writable."""
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        return False
    if not os.access(path, os.W_OK):
        return False
    return True

def verify_volume_mount(container, expected_host_path: str) -> bool:
    """Verify that the container has the correct volume mount."""
    try:
        container.reload()
        mounts = container.attrs.get("Mounts", [])
        for mount in mounts:
            if mount.get("Destination") == "/mlflow_data":
                source = mount.get("Source", "")
                # Normalize paths for comparison (handle symlinks, trailing slashes, etc.)
                expected = os.path.normpath(expected_host_path)
                actual = os.path.normpath(source)
                if actual == expected:
                    return True
                else:
                    print(f"    WARNING: Mount source mismatch!")
                    print(f"      Expected: {expected}")
                    print(f"      Actual: {actual}")
                    return False
        return False
    except Exception as e:
        print(f"    ERROR: Could not verify volume mount: {e}")
        return False

def start_container():
    client = docker.from_env()
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(project_dir, "mlflow.env")

    load_dotenv(env_path)

    container_name = "mlflow_global_server"
    image_name = "mlflow_global_setup:latest"

    # Read external volume path
    host_data_dir = os.getenv("MLFLOW_DATA_DIR")
    if not host_data_dir:
        print("ERROR: MLFLOW_DATA_DIR not set in mlflow.env")
        return

    # Expand user path (~/mlflow -> /Users/sdatta/mlflow)
    host_data_dir = os.path.expanduser(host_data_dir)
    
    # Ensure path is absolute
    host_data_dir = os.path.abspath(host_data_dir)
    
    # Create directory if it doesn't exist
    os.makedirs(host_data_dir, exist_ok=True)
    
    # Validate path
    if not validate_path(host_data_dir):
        print(f"ERROR: Path validation failed for {host_data_dir}")
        print(f"  - Exists: {os.path.exists(host_data_dir)}")
        print(f"  - Is directory: {os.path.isdir(host_data_dir) if os.path.exists(host_data_dir) else 'N/A'}")
        print(f"  - Writable: {os.access(host_data_dir, os.W_OK) if os.path.exists(host_data_dir) else 'N/A'}")
        return
    
    print(f"✓ Validated host data directory: {host_data_dir}")

    # Port configuration
    try:
        host_port = int(os.getenv("MLFLOW_PORT", "5000"))
    except ValueError:
        host_port = 5000

    if is_port_in_use(host_port):
        print(f"Port {host_port} is already in use. Change MLFLOW_PORT in mlflow.env.")
        return

    # Stop existing container
    try:
        old = client.containers.get(container_name)
        print("Stopping existing container...")
        old.stop()
        old.remove()
    except docker.errors.NotFound:
        pass

    # Read MLflow environment variables
    backend_store_uri = os.getenv("MLFLOW_BACKEND_STORE_URI")
    default_artifact_root = os.getenv("MLFLOW_DEFAULT_ARTIFACT_ROOT")
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    
    print(f"\n{'='*60}")
    print(f"Container Configuration:")
    print(f"{'='*60}")
    print(f"  Container name: {container_name}")
    print(f"  Image: {image_name}")
    print(f"  Host port: {host_port}")
    print(f"  Host data directory: {host_data_dir}")
    print(f"  Container mount point: /mlflow_data")
    print(f"  Backend store URI: {backend_store_uri}")
    print(f"  Artifact root: {default_artifact_root}")
    print(f"{'='*60}\n")
    
    print(f"Starting MLflow container on port {host_port}...")
    
    # Volume mount configuration - using bind mount format
    volume_config = {
        host_data_dir: {
            "bind": "/mlflow_data",
            "mode": "rw"
        }
    }
    
    print(f"Volume mount configuration:")
    print(f"  Host: {host_data_dir}")
    print(f"  Container: /mlflow_data")
    print(f"  Mode: rw")

    container = client.containers.run(
        image=image_name,
        name=container_name,
        environment={
            "MLFLOW_BACKEND_STORE_URI": backend_store_uri,
            "MLFLOW_DEFAULT_ARTIFACT_ROOT": default_artifact_root,
            "MLFLOW_TRACKING_URI": tracking_uri,
        },
        ports={f"5000/tcp": host_port},
        volumes=volume_config,
        detach=True,
        restart_policy={"Name": "always"},
    )

    # Verify the volume mount was created correctly
    print(f"\n✓ Container started: {container.name}")
    print(f"✓ MLflow running at http://localhost:{host_port}")
    print(f"✓ Volume mount: {host_data_dir} -> /mlflow_data")
    
    # Verify mount by inspecting container
    print(f"\n{'='*60}")
    print(f"Volume Mount Verification:")
    print(f"{'='*60}")
    try:
        container.reload()
        mounts = container.attrs.get("Mounts", [])
        if mounts:
            mount_found = False
            for mount in mounts:
                if mount.get("Destination") == "/mlflow_data":
                    mount_found = True
                    print(f"  ✓ Found /mlflow_data mount:")
                    print(f"    Source: {mount.get('Source', 'N/A')}")
                    print(f"    Destination: {mount.get('Destination', 'N/A')}")
                    print(f"    Type: {mount.get('Type', 'N/A')}")
                    print(f"    Mode: {mount.get('Mode', 'N/A')}")
                    
                    # Verify the mount source matches expected path
                    if verify_volume_mount(container, host_data_dir):
                        print(f"  ✓ Mount source verified: matches expected path")
                    else:
                        print(f"  ⚠ Mount source verification failed!")
            if not mount_found:
                print(f"  ⚠ WARNING: /mlflow_data mount not found in container!")
                print(f"    Available mounts: {[m.get('Destination') for m in mounts]}")
        else:
            print(f"  ⚠ WARNING: No volume mounts found in container!")
    except Exception as e:
        print(f"  ⚠ Could not verify volume mount: {e}")
    print(f"{'='*60}")
    
    print(f"\n✓ All MLflow data will be persisted to: {host_data_dir}")

    # Create sourceable shell script for environment setup
    env_script_path = os.path.join(project_dir, "mlflow_env.sh")
    tracking_uri = f"http://localhost:{host_port}"
    with open(env_script_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"# Generated by run_container.py - Source this file to configure MLflow CLI\n")
        f.write(f"export MLFLOW_TRACKING_URI={tracking_uri}\n")

    print(f"\n To use MLflow CLI with this server, run:")
    print(f"   source mlflow_env.sh")

if __name__ == "__main__":
    start_container()
