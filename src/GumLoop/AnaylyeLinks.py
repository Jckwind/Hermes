"""
This module interacts with the Gumloop API to start and monitor a flow.

It provides functionality to start a Gumloop flow using input from a file,
check the status of a running flow, and process the results.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional
import os

import requests



API_KEY = os.environ.get('GUMLOOP_API_KEY')
# Constants
API_BASE_URL = "https://api.gumloop.com/api/v1"
START_PIPELINE_ENDPOINT = f"{API_BASE_URL}/start_pipeline"
GET_PL_RUN_ENDPOINT = f"{API_BASE_URL}/get_pl_run"

# Configuration
CONFIG_FILE = Path(__file__).parent / "config.json"


class ConfigLoader:
    """Handles loading of configuration from a JSON file."""

    @staticmethod
    def load_config() -> Dict[str, str]:
        """Load configuration from a JSON file."""
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {CONFIG_FILE}")


class Logger:
    """Handles logging throughout the application."""

    @staticmethod
    def info(message: str) -> None:
        """Log an info message."""
        print(f"INFO: {message}")

    @staticmethod
    def error(message: str) -> None:
        """Log an error message."""
        print(f"ERROR: {message}")


class GumloopAPIClient:
    """A client to interact with the Gumloop API."""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config['API_KEY']}",
            "Content-Type": "application/json"
        }

    def start_flow(self, links_content: str) -> Optional[str]:
        """
        Start a Gumloop flow with the provided links content.

        Args:
            links_content (str): Content of the links file.

        Returns:
            Optional[str]: The run ID if successful, None otherwise.
        """
        payload = {
            "user_id": self.config["USER_ID"],
            "saved_item_id": self.config["SAVED_ITEM_ID"],
            "pipeline_inputs": [{"input_name": "Links", "value": links_content}]
        }

        try:
            response = requests.post(START_PIPELINE_ENDPOINT, json=payload, headers=self.headers)
            response.raise_for_status()
            run_id = response.json()["run_id"]
            Logger.info(f"Flow started successfully. Run ID: {run_id}")
            return run_id
        except requests.RequestException as e:
            Logger.error(f"Error starting flow: {e}")
            return None

    def get_flow_status(self, run_id: str) -> Optional[Dict]:
        """
        Check the status of a running Gumloop flow.

        Args:
            run_id (str): The ID of the flow run.

        Returns:
            Optional[Dict]: The status response if successful, None otherwise.
        """
        params = {
            "run_id": run_id,
            "user_id": self.config["USER_ID"]
        }

        try:
            response = requests.get(GET_PL_RUN_ENDPOINT, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            Logger.error(f"Error getting flow status: {e}")
            return None


class FlowManager:
    """Manages the execution and monitoring of Gumloop flows."""

    def __init__(self, api_client: GumloopAPIClient):
        self.api_client = api_client

    def start_flow(self, links_file: str) -> Optional[str]:
        """
        Start a Gumloop flow with input from the specified file.

        Args:
            links_file (str): Path to the file containing links.

        Returns:
            Optional[str]: The run ID if successful, None otherwise.
        """
        try:
            with open(links_file, "r") as file:
                links_content = file.read()
        except FileNotFoundError:
            Logger.error(f"File not found - {links_file}")
            return None

        return self.api_client.start_flow(links_content)

    def monitor_flow(self, run_id: str, check_interval: int = 5) -> None:
        """
        Monitor the status of a Gumloop flow until completion.

        Args:
            run_id (str): The ID of the flow run to monitor.
            check_interval (int): Time in seconds between status checks.
        """
        while True:
            status = self.api_client.get_flow_status(run_id)
            if not status:
                Logger.error("Failed to get flow status. Exiting.")
                return

            Logger.info(f"Current status: {status['state']}")

            if status["state"] == "DONE":
                Logger.info("Flow completed successfully!")
                Logger.info("Response:")
                Logger.info(json.dumps(status, indent=2))
                break
            elif status["state"] == "FAILED":
                Logger.error("Flow failed!")
                Logger.error("Error log:")
                Logger.error(status.get("log", "No error log available"))
                break
            else:
                Logger.info(f"Waiting for {check_interval} seconds before checking again...")
                time.sleep(check_interval)


def main():
    """Main function to run the Gumloop flow process."""
    config = ConfigLoader.load_config()
    api_client = GumloopAPIClient(config)
    flow_manager = FlowManager(api_client)

    links_file = "Links.txt"  # Assuming the file is in the same directory

    Logger.info("Starting Gumloop flow...")
    run_id = flow_manager.start_flow(links_file)
    if run_id:
        flow_manager.monitor_flow(run_id)


if __name__ == "__main__":
    main()
