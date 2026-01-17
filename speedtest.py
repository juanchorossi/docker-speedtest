#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import json
import requests
from datetime import datetime, timezone
import pytz
import os
import time
import dns.resolver
from supabase import create_client, Client

def send_telegram_message(message):
    """Send provided message to the Telegram chat specified by chat_id."""
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not telegram_token or not telegram_chat_id:
        print("Telegram credentials not configured, skipping notification.")
        return

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
    error_reporting = os.getenv('ERROR_REPORTING', 'FALSE').lower() == 'true'
    if error_reporting:
        send_telegram_message(error_message)

def check_speed_threshold(download_mbps, threshold_mbps):
    """Check if download speed is below threshold and send alert."""
    if threshold_mbps and download_mbps < threshold_mbps:
        alert_message = (
            f"*Speed Alert*\n\n"
            f"Download speed is below threshold!\n"
            f"Current: *{download_mbps:.2f} Mbps*\n"
            f"Threshold: *{threshold_mbps:.2f} Mbps*"
        )
        send_telegram_message(alert_message)
        return True
    return False

def get_supabase_client() -> Client:
    """Create and return a Supabase client."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials are not configured properly.")

    return create_client(supabase_url, supabase_key)

def measure_dns(domain="google.com", server="1.1.1.1"):
    """Measure DNS resolution time for a specific server."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    resolver.timeout = 5
    resolver.lifetime = 5
    start = time.time()
    try:
        resolver.resolve(domain, 'A')
        return round((time.time() - start) * 1000, 2)
    except Exception:
        return None

# Main script execution
if __name__ == "__main__":
    try:
        # Get speed threshold (optional)
        threshold_str = os.getenv('SPEED_THRESHOLD_MBPS')
        speed_threshold = float(threshold_str) if threshold_str else None

        # Initialize Supabase client
        supabase = get_supabase_client()

        print("Running speedtest...")

        # Execute speedtest CLI
        result = subprocess.check_output(["/usr/bin/speedtest", "--format=json"], timeout=120).decode('utf-8')
        print("Result from speedtest:")
        print(result)

        if result.strip() == "":
            raise ValueError("No output received from speedtest.")

        data = json.loads(result)

        # Extract and convert data
        download_mbps = data['download']['bandwidth'] / 125000  # Convert bytes/s to Mbps
        upload_mbps = data['upload']['bandwidth'] / 125000      # Convert bytes/s to Mbps
        ping_ms = data['ping']['latency']
        ping_jitter = data['ping']['jitter']
        ping_low = data['ping']['low']
        ping_high = data['ping']['high']
        isp = data['isp']
        ip = data['interface']['externalIp']

        # Measure DNS resolution times
        dns_cloudflare_ms = measure_dns(server="1.1.1.1")
        dns_google_ms = measure_dns(server="8.8.8.8")
        dns_isp_ms = measure_dns(server="190.13.208.2")

        print(f"Download: {download_mbps:.2f} Mbps")
        print(f"Upload: {upload_mbps:.2f} Mbps")
        print(f"Ping: {ping_ms:.2f} ms (jitter: {ping_jitter:.2f}, low: {ping_low:.2f}, high: {ping_high:.2f})")
        print(f"DNS Cloudflare: {dns_cloudflare_ms} ms")
        print(f"DNS Google: {dns_google_ms} ms")
        print(f"DNS ISP: {dns_isp_ms} ms")

        # Prepare the payload for Supabase
        payload = {
            "download_mbps": round(download_mbps, 2),
            "upload_mbps": round(upload_mbps, 2),
            "ping_ms": round(ping_ms, 2),
            "ping_jitter": round(ping_jitter, 2),
            "ping_low": round(ping_low, 2),
            "ping_high": round(ping_high, 2),
            "dns_cloudflare_ms": dns_cloudflare_ms,
            "dns_google_ms": dns_google_ms,
            "dns_isp_ms": dns_isp_ms,
            "isp": isp,
            "ip": ip,
        }

        # Insert data into Supabase
        response = supabase.table('speedtest_results').insert(payload).execute()

        if response.data:
            print("Data successfully sent to Supabase.")
        else:
            raise ValueError(f"Error sending data to Supabase: {response}")

        # Check speed threshold and send alert if needed
        if speed_threshold:
            check_speed_threshold(download_mbps, speed_threshold)

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing speedtest: Command returned non-zero exit status {e.returncode}."
        if e.output:
            error_message += f" Output: {e.output.decode().strip()}"
        report_error(error_message)
    except subprocess.TimeoutExpired:
        report_error("Timeout expired when executing speedtest.")
    except KeyboardInterrupt:
        report_error("Script manually interrupted.")
    except Exception as e:
        report_error(f"An error occurred: {e}")
