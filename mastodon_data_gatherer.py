import requests
import time
import multiprocessing
from consts_and_methods import get_headers, save_data, fetch_paginated_data, log_info, setup_logging, seen_accounts, to_process_accounts, gathered_data, INSTANCES


def get_following_of_account(instance_url, account_id, account_name, depth, max_depth=3, max_following=1000):
    if account_id in seen_accounts:
        if gathered_data[account_name]["following"] != None:
            log_info(f"Skipping account {account_id}, already processed.")
            return []
    
    seen_accounts.add(account_id)

    url = f"{instance_url}/api/v1/accounts/{account_id}/following"
    response = requests.get(url, headers=get_headers(instance_url))
    if response.status_code == 200:
        gathered_data[account_name] = {"followers": None, "following": None}
        log_info(f"Fetching following for {account_name} ({depth}) from {instance_url}")
    else:
        log_info("Error verifying credentials.")
        return []
    
    following = fetch_paginated_data(url, instance_url, max_following)
    formatted_following = []
    next_depth = depth+1
    for profile in following:
        if profile["id"] not in seen_accounts and next_depth <= max_depth:
            display_name = profile["acct"]
            if (profile["acct"] == ''):
                display_name = profile["username"]
            to_process_accounts.add((profile["id"], display_name, next_depth))
        formatted_following.append({
            "id": profile["id"],
            "username": profile["username"],
            "acct": profile["acct"],
            "display_name": profile["display_name"],
            "bot": profile["bot"],
            "created_at": profile["created_at"],
            "followers_count": profile["followers_count"],
            "following_count": profile["following_count"]
        })

    gathered_data[account_name]["following"] = formatted_following


def get_followers_of_account(instance_url, account_id, account_name, depth, max_depth=3, max_followers=1000):
    if account_id in seen_accounts:
        if gathered_data[account_name]["followers"] != None:
            log_info(f"Skipping account {account_id}, already processed.")
            return []
    
    seen_accounts.add(account_id)

    url = f"{instance_url}/api/v1/accounts/{account_id}/followers"
    response = requests.get(url, headers=get_headers(instance_url))
    if response.status_code == 200:
        log_info(f"Fetching followers for {account_name} ({depth}) from {instance_url}")
    else:
        log_info("Error verifying credentials.")
        return []
    
    following = fetch_paginated_data(url, instance_url, max_followers)
    formatted_following = []
    next_depth = depth+1
    for profile in following:
        if profile["id"] not in seen_accounts and next_depth <= max_depth:
            display_name = profile["acct"]
            if (profile["acct"] == ''):
                display_name = profile["username"]
            to_process_accounts.add((profile["id"], display_name, next_depth))
        formatted_following.append({
            "id": profile["id"],
            "username": profile["username"],
            "acct": profile["acct"],
            "display_name": profile["display_name"],
            "bot": profile["bot"],
            "created_at": profile["created_at"],
            "followers_count": profile["followers_count"],
            "following_count": profile["following_count"]
        })

    gathered_data[account_name]["followers"] = formatted_following


def process_instance(instance):
    instance_name = instance.replace("https://", "").replace(".", "_")

    url = f"{instance}/api/v1/accounts/verify_credentials"
    current_depth = 1
    response = requests.get(url, headers=get_headers(instance))
    account_id = response.json()["id"]
    account_name = response.json()["acct"]
    if account_name == '':
        account_name = response.json()["acct"]
    get_following_of_account(instance, account_id, account_name, current_depth)
    get_followers_of_account(instance, account_id, account_name, current_depth)
    accounts_processed = 0

    while len(to_process_accounts) > 0:
        account_id, account_name, depth = to_process_accounts.pop()
        log_info(f"Fetching neighbours for {account_name} from {instance}")
        get_following_of_account(instance, account_id, account_name, depth)
        get_followers_of_account(instance, account_id, account_name, depth)

        accounts_processed += 1
        if accounts_processed == 50:
            accounts_processed = 0
            save_data(gathered_data, f"network_data-{instance_name}.json")
            log_info(f"Saved data for {instance}")
            log_info(f"Current number of accounts = {len(gathered_data.keys())}")

        time.sleep(1)


if __name__ == "__main__":
    try:
        setup_logging()
        with multiprocessing.Pool(processes=len(INSTANCES)) as pool:
            pool.map(process_instance, INSTANCES)
    except Exception as e:
        log_info(f"Error occurred: {e}")

    log_info("Data collected for all instances.")