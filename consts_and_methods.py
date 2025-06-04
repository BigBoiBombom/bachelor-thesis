import time
import json
import requests
import logging
import sys
from datetime import datetime

INSTANCES = [
    "https://musicworld.social",
    "https://ioc.exchange",
    "https://hostux.social"
]
ACCESS_TOKENS = {
    "https://mastodon.social": "1BjOwLRxNOmHHItnsU05yFIlnpiWd2A3fmXrUcRqraE",
    "https://musicworld.social": "lu4qNA5lG8CzWvQvF6GTqEg1j1KpMVJSer6cjkq-e8g",
    "https://ioc.exchange": "bAk_j0V9d3N3kvRvPvnjbCK9XYIRhcMC3VLL0FfrI7Y",
    "https://hostux.social": "QtM5SzpcjAAZzVLffkA0VnLvqIk_Bnoa_Gd5wjQhYgc",
    "https://techhub.social": "DkPMqb4Of-N-b3__8Lo-GhmTEUA7bD1tbtOcp2OHZoI"
}

seen_accounts = set()
to_process_accounts = set()
gathered_data = {}


def get_headers(instance_url):
    return {
        "Authorization": f"Bearer {ACCESS_TOKENS[instance_url]}"
    }


def save_data(data, filename, mode='w'):
    with open(f'data/{filename}', mode) as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")


def check_rate_limit(response):
    remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
    reset_time_str = response.headers.get('X-RateLimit-Reset', time.time())

    try:
        reset_time = datetime.fromisoformat(reset_time_str.replace('Z', '+00:00')).timestamp()
    except Exception:
        reset_time = time.time()

    if remaining <= 5:
        sleep_time = max(reset_time - time.time(), 0)
        print(f"Approaching rate limit. Sleeping for {sleep_time + 1} seconds...")
        time.sleep(sleep_time + 1)
    else:
        print(f"Remaining rate limit: {remaining}")


def exponential_backoff(attempts):
    delay = min(2 ** attempts, 60)
    print(f"Backing off for {delay} seconds")
    time.sleep(delay)


def fetch_paginated_data(url, instance_url, maxAccounts=1000):
    data = []
    attempts = 0
    while url:
        try:
            response = requests.get(url, headers=get_headers(instance_url))

            check_rate_limit(response)

            if response.status_code == 200:
                data.extend(response.json())
                
                if "next" in response.links:
                    url = response.links["next"]["url"]
                else:
                    print(f"All pages fetched for {url}")
                    url = None
            else:
                print(f"Error fetching data from {url}. Status: {response.status_code}")
                break

            if len(data) >= maxAccounts:
                print(f"Reached max accounts limit: {maxAccounts}. Stopping fetch.")
                break

            time.sleep(0.5)
            attempts = 0

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            attempts += 1
            if attempts > 5:
                print("Max retries reached. Exiting.")
                break
            exponential_backoff(attempts)

    return data


def setup_logging(log_file="program.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging setup complete.")


def log_info(message):
    logging.info(message)