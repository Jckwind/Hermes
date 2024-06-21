import requests
import json
import time

API_KEY = "36fe11b32dbb4d5a9b77b67f59596046"  # Your API key
USER_ID = "Aw2TmLpSXcX6tDv0jWiLZ8QzwR13"  # Your user ID
SAVED_ITEM_ID = "xaKWePBCWrDVmWtoHmCwdB"  # Your saved item ID

def start_gumloop_flow():
    """Sends a request to start a Gumloop flow with input from 'links.txt'."""

    url = "https://api.gumloop.com/api/v1/start_pipeline"

    with open("links.txt", "r") as file:
        links_content = file.read()

    payload = {
        "user_id": USER_ID,
        "saved_item_id": SAVED_ITEM_ID,
        "pipeline_inputs": [{"input_name": "Links", "value": links_content}]
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Flow started successfully: {response.json()}")
        run_id = response.json()["run_id"]
        return run_id
    else:
        print(f"Error starting flow: {response.text}")
        return None

def get_flow_status(run_id):
    """Checks the status of a running Gumloop flow."""

    url = f"https://api.gumloop.com/api/v1/get_pl_run?run_id={run_id}&user_id={USER_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting flow status: {response.text}")
        return None

# Example usage:
run_id = start_gumloop_flow()
if run_id:
    while True:
        status = get_flow_status(run_id)
        if status["state"] == "DONE":
            print("Flow completed successfully!")
            # Process outputs from 'status["outputs"]' if needed
            break
        elif status["state"] == "FAILED":
            print("Flow failed!")
            # Handle error based on 'status["log"]' if needed
            break
        else:
            print(f"Flow status: {status['state']}")
            # You can adjust the sleep time here
            time.sleep(5)  # Check again in 5 seconds