#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import json
import requests
from datetime import datetime
import pytz
import os

# Load environment variables for Tinybird and Telegram
tinybird_token = os.getenv('TINYBIRD_TOKEN')
tinybird_base_url = os.getenv('TINYBIRD_BASE_URL', 'https://api.us-east.aws.tinybird.co')
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
error_reporting = os.getenv('ERROR_REPORTING', 'FALSE').lower() == 'true'

tinybird_endpoint = "/v0/events?name=speedtest"
tinybird_url = f"{tinybird_base_url}{tinybird_endpoint}"

def send_telegram_message(message):
    """Send provided message to the Telegram chat specified by chat_id."""
    telegram_api_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(telegram_api_url, json=payload)
        response.raise_for_status()
    except Exception as error:
        print(f"Error sending message to Telegram: {error}")

def report_error(error_message):
    """Report an error message if error reporting is enabled."""
    print(error_message)
    if error_reporting:
        send_telegram_message(error_message)

try:
    if not tinybird_token:
        raise ValueError("Tinybird credentials are not configured properly.")

    print("Running speedtest-cli...")
    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {tinybird_token}"})
        
        # Execute speedtest-cli
        result = subprocess.check_output(["speedtest-cli", "--json"], timeout=120).decode('utf-8')
        print("Result from speedtest-cli:")
        print(result)

        if result.strip() == "":
            raise ValueError("No output received from speedtest-cli.")

        data = json.loads(result)
        
        print("Extracted data from JSON:")
        print(data)

        # Date and time processing
        dt_object = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        dt_utc = dt_object.replace(tzinfo=pytz.utc)
        local_dt = dt_utc.astimezone(pytz.timezone('America/Argentina/Buenos_Aires'))
        dt_serializable = local_dt.isoformat()

        # Prepare the payload
        payload = {
            "time": dt_serializable,
            "download": data['download'] / 1000000,  # Convert to Mbps
            "upload": data['upload'] / 1000000,      # Convert to Mbps
            "ping": data['ping'],
            "isp": data['client']['isp'],
            "ip": data['client']['ip'],
        }
        print(payload)

        # Send data to Tinybird
        response = session.post(tinybird_url, json=payload)
        if response.status_code == 202:
            print("Data successfully sent to Tinybird.")
        else:
            raise ValueError(f"Error sending data to Tinybird. Status code: {response.status_code}")

except subprocess.CalledProcessError as e:
    report_error(f"Error executing speedtest-cli: {e}")
except subprocess.TimeoutExpired:
    report_error("Timeout expired when executing speedtest-cli.")
except KeyboardInterrupt:
    report_error("Script manually interrupted.")
except Exception as e:  # Catch other exceptions such as failing to read the TOKEN or other runtime exceptions
    report_error(f"An error occurred: {e}")