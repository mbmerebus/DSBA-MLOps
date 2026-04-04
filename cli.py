import argparse
import os
import secrets
import subprocess

# Base directory of the project, resolved relative to this file (at base too)
# otherwise we can get path file erros such as "no file found in directory"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#CLI made so all important commands to take the tool online are readily available to the provider.
# The goal is to make it easy with a well defined and verbose set of commands so the provider knows what
# they are doing and what is happening. Same syntax and help makes for better clarity
# Also the provider can have more control on the deployment and operation of the services/whole tool

# -- Build commands -- PREREQUISITE --

def generate_env():
    """
    Generate a .env file with secure random secrets at the project root.
    Warns if a .env already exists to avoid overwriting intentionally set values.
    """
    #print(f"BASE_DIR: {BASE_DIR}") #DEBUG
    print(f"Looking for .env at: {os.path.join(BASE_DIR, '.env')}")
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        print(f".env already exists at {env_path}. Delete it first if you want to regenerate.")
        return

    # crypto
    content = f"""
        JWT_SECRET={secrets.token_hex(32)}
        ESTIMATE_ENCRYPTION_KEY={secrets.token_hex(32)}
        PASSWORD_PEPPER={secrets.token_hex(32)}
    """

    with open(env_path, "w") as f:
        f.write(content)
    print(f".env generated at {env_path}")


def train(data_path):
    """
    Verifies that the input data file exists before launching training.
    This helps avoids cryptic errors deep in the training pipeline if the file is missing.
    """

    if not os.path.isfile(data_path):
        print(f"Error: data file not found at {data_path}")
        return

    print(f"Data found at {data_path}. Starting training...")

    # We import here and not before so we can avoid reloading
    # dependancies at each CLI call -> less time taken
    import sys

    sys.path.insert(0, os.path.join(BASE_DIR, "src", "training"))
    from train import train_model
    from datetime import datetime

    model_output = os.path.join(
        BASE_DIR,
        f"src/scoring/model_storage/model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    )
    train_model(data_path, model_output)

# -- Whole tool handling --

def start():
    """
    Build and start all services using Docker Compose.
    Equivalent to: docker-compose down && docker-compose up --build
    """
    print("Stopping any running containers...")
    subprocess.run(["docker-compose", "down"], cwd=BASE_DIR, check=True)
    print("Building and starting all services...")
    subprocess.run(["docker-compose", "up", "--build"], cwd=BASE_DIR, check=True)


def stop():
    """
    Stop all running services using Docker Compose.
    Equivalent to: docker-compose down
    """
    print("Stopping all services...")
    subprocess.run(["docker-compose", "down"], cwd=BASE_DIR, check=True)
    print("All services stopped.")

# -- Services handling--

def start_service(service):
    """
    Rebuild and restart a specific service without affecting the others.
    Useful during development to apply changes to a single container.
    """
    print(f"(Re)starting {service}...")
    subprocess.run(["docker-compose", "up", "--build", "-d", service], cwd=BASE_DIR, check=True)
    print(f"{service} restarted.")


def stop_service(service):
    """
    Stop a specific service without affecting the others.
    """
    print(f"Stopping {service}...")
    subprocess.run(["docker-compose", "stop", service], cwd=BASE_DIR, check=True)
    print(f"{service} stopped.")

# -- MAIN --

def main():
    parser = argparse.ArgumentParser(description="DSBA-MLOps CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Command: generate-env
    subparsers.add_parser("generate-env", help="Generate a .env file with secure random secrets")

    # Command: train
    train_parser = subparsers.add_parser("train", help="Train the valuation model")
    train_parser.add_argument("--data", required=True, help="Path to the DVF input CSV file")


    # Command: start tool
    subparsers.add_parser("start", help="Build and start all services (docker-compose up --build)")
    # Command: stop tool
    subparsers.add_parser("stop", help="Stop all running services (docker-compose down)")

    # Command: restart-service
    restart_parser = subparsers.add_parser("start-service", help="Rebuild and restart a specific service")
    restart_parser.add_argument("service", help="Service name (e.g. webui, gateway, auth, history, scoring-api)")

    # Command: stop-service
    stop_service_parser = subparsers.add_parser("stop-service", help="Stop a specific service")
    stop_service_parser.add_argument("service", help="Service name (e.g. webui, gateway, auth, history, scoring-api)")



    args = parser.parse_args()
    #print(f"Command received: {args.command}") #DEBUG

    if args.command == "generate-env":
        generate_env()
    elif args.command == "train":
        train(args.data)
    elif args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "start-service":
        start_service(args.service)
    elif args.command == "stop-service":
        stop_service(args.service)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()