import csv
import requests
import time
import os
import sys

# Get token, device ID, location ID, and virtual switch ID from environment variables
TOKEN = os.environ.get('SMARTTHINGS_TOKEN')
DEVICE_ID = os.environ.get('DEVICE_ID')
LOCATION_ID = os.environ.get('LOCATION_ID')
VIRTUAL_SWITCH_ID = os.environ.get('VIRTUAL_SWITCH_ID')

if not all([TOKEN, DEVICE_ID, LOCATION_ID, VIRTUAL_SWITCH_ID]):
    print("Error: Please set SMARTTHINGS_TOKEN, DEVICE_ID, LOCATION_ID, and VIRTUAL_SWITCH_ID environment variables.")
    sys.exit(1)

# API URL with locationId query parameter
API_URL = f"https://api.smartthings.com/v1/rules?locationId={LOCATION_ID}"

# CSV file containing holiday dates
CSV_FILE = "yom_tov_dates.csv"

# Time zone for triggers (adjust as needed)
TIME_ZONE = "America/New_York"

def get_existing_rules():
    """
    Fetches existing rules from the API and returns them as a dictionary.
    
    Returns:
    dict: A dictionary where the keys are the rule names and the values are the rule IDs.
    """
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(API_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'items' in data and isinstance(data['items'], list):
                    return {rule['name']: rule['id'] for rule in data['items']}
                else:
                    print("Warning: Response does not contain a list of rules.")
                    return {}
            except ValueError:
                print("Warning: Response is not valid JSON. Content:", response.text)
                return {}
        else:
            print(f"Warning: Could not fetch existing rules: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Warning: Error fetching existing rules: {e}")
        return {}

def create_rule(name, date_str):
    if name in existing_rules:
        print(f"Rule '{name}' already exists with ID: {existing_rules[name]}. Skipping.")
        return
    try:
        year_int, month_int, day_int = map(int, date_str.split('-'))
    except ValueError:
        print(f"Error: Invalid date format for '{name}': {date_str}. Expected YYYY-MM-DD.")
        return

    # Construct the rule JSON with conditions for virtual switch and date
    rule = {
        "name": name,
        "timeZoneId": TIME_ZONE,
        "actions": [
            {
                "if": {
                    "and": [
                        {
                            "equals": {
                                "left": {
                                    "device": {
                                        "devices": [VIRTUAL_SWITCH_ID],
                                        "component": "main",
                                        "capability": "switch",
                                        "attribute": "switch"
                                    }
                                },
                                "right": {"string": "on"}
                            }
                        },
                        {
                            "equals": {
                                "left": {
                                    "date": {
                                        "timeZoneId": TIME_ZONE,
                                        "reference": "Today"
                                    }
                                },
                                "right": {
                                    "date": {
                                        "timeZoneId": TIME_ZONE,
                                        "year": year_int,
                                        "month": month_int,
                                        "day": day_int,
                                    }
                                }
                            }
                        }
                    ],
                    "then": [
                        {
                            "command": {
                                "devices": [DEVICE_ID],
                                "commands": [
                                    {
                                        "component": "main",
                                        "capability": "samsungce.sabbathMode",
                                        "command": "on",
                                        "arguments": []
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }

    # Set headers with authorization token
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # Send POST request to create the rule
    try:
        response = requests.post(API_URL, json=rule, headers=headers)
        if response.status_code in (200, 201):
            rule_id = response.json().get('id', 'unknown')
            print(f"Successfully created rule '{name}' with ID: {rule_id}")
        else:
            print(f"Failed to create rule '{name}': {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating rule '{name}': {e}")

    # Delay to respect rate limits
    time.sleep(1)

# Main script
existing_rules = get_existing_rules()

try:
    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        expected_headers = {'Year', 'Yom Tov', 'Start of First Days', 'Start of Last Day (After Chol Hamoed)'}
        if not expected_headers.issubset(reader.fieldnames):
            print("Error: CSV must contain headers: Year, Yom Tov, Start of First Days, Start of Last Day (After Chol Hamoed)")
            sys.exit(1)

        for row in reader:
            year = row['Year']
            yom_tov = row['Yom Tov']
            first_days_date = row['Start of First Days']
            last_day_date = row['Start of Last Day (After Chol Hamoed)']

            # Process Start of First Days
            if not first_days_date:
                print(f"Skipping {yom_tov} ({year}) First Days: No start date provided.")
            else:
                name = f"{yom_tov} First Days ({year})" if last_day_date else f"{yom_tov} ({year})"
                create_rule(name, first_days_date)

            # Process Start of Last Day (After Chol Hamoed)
            if not last_day_date:
                print(f"Skipping {yom_tov} ({year}) Last Day: No last day date provided.")
            else:
                name = f"{yom_tov} Last Day ({year})"
                create_rule(name, last_day_date)

except FileNotFoundError:
    print(f"Error: CSV file '{CSV_FILE}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)