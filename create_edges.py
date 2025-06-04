import json
import csv

graph_data = set()

def JSON_to_graph_edges(input_json, output_csv):
    with open(input_json, "r", encoding="utf-8") as infile:
        data = json.load(infile)
        
        with open(output_csv, "w", newline='', encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["source", "target"])
            duplicate_check = set()
            
            for record in data.items():
                target_name = record[0]
                print(f"Processing followers of: {target_name}")
                for follower in record[1]["followers"]:
                    source_name = follower["acct"]
                    if (source_name, target_name) not in duplicate_check:
                        duplicate_check.add((source_name, target_name))
                        writer.writerow([source_name, target_name])
                    
                print(f"Processing followings of: {target_name}")
                for following in record[1]["following"]:
                    source_name = following["acct"]
                    if (target_name, source_name) not in duplicate_check:
                        duplicate_check.add((target_name, source_name))
                        writer.writerow([target_name, source_name])
    print(f"CSV file '{output_csv}' has been created.")

if __name__ == "__main__":
    input_json = "network_data-hostux_social.json"
    output_csv = "hostux_social-edges.csv"
    
    JSON_to_graph_edges(input_json, output_csv)
    
    input_json = "network_data-ioc_exchange.json"
    output_csv = "ioc_exchange-edges.csv"
    
    JSON_to_graph_edges(input_json, output_csv)
    
    input_json = "network_data-musicworld_social.json"
    output_csv = "musicworld_social-edges.csv"
    
    JSON_to_graph_edges(input_json, output_csv)