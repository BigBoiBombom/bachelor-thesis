import json
import csv


def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def parse_username(username, instance_name):
    if "@" in username:
        name = username
        instance = username.split("@", -1)[-1]
    else:
        name = username
        instance = instance_name.replace("_", ".")
    return name, instance


def extract_nodes(account_data, instance_name):
    nodes = {}

    def add_username(username):
        full_username, instance = parse_username(username, instance_name)
        if full_username not in nodes:
            nodes[full_username] = {
                "name": full_username,
                "instance": instance,
            }

    for account, details in account_data.items():
        add_username(account)
        for follower in details.get("followers", []):
            follower_name = follower.get("acct")
            if follower_name:
                add_username(follower_name)

        for following in details.get("following", []):
            following_name = following.get("acct")
            if following_name:
                add_username(following_name)

    return list(nodes.values())


def save_nodes_to_csv(nodes, output_file):
    fieldnames = ['name', 'instance']
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(nodes)


if __name__ == "__main__":
    for instance_file in ['hostux_social', 'ioc_exchange', 'musicworld_social']:
        output_file = f'{instance_file}-nodes.csv'

        account_data = load_json(f'network_data-{instance_file}.json')
        nodes = extract_nodes(account_data, instance_file)
        save_nodes_to_csv(nodes, output_file)

        print(f"Saved {len(nodes)} nodes to {output_file}")