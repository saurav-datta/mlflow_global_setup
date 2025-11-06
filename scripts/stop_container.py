import docker

def stop_container():
    client = docker.from_env()
    container_name = "mlflow_global_server"

    try:
        container = client.containers.get(container_name)
        print(f"Stopping container '{container_name}'...")
        container.stop()
        container.remove()
        print(f"Container '{container_name}' stopped and removed.")
    except docker.errors.NotFound:
        print(f"No running container named '{container_name}' was found.")
    except Exception as e:
        print(f"Failed to stop container: {e}")

if __name__ == "__main__":
    stop_container()
