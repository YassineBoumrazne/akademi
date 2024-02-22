import json
import subprocess
import time
import os
from datetime import datetime

def save_to_hdfs(json_data, filename, hdfs_path):
    # Create a unique name for the JSON file based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    json_filename = f"{timestamp}_{filename}".replace(" ", "")

    with open(json_filename, 'w') as json_file:
        json.dump(json_data, json_file)
    print(json_filename)
    subprocess.run(['hdfs', 'dfs', '-put', json_filename, hdfs_path])

    print(f'Saved JSON file to HDFS at {hdfs_path}')


def monitor_folder_and_save_to_hdfs(folder_path):
    hdfs_path = '/user/student/'
    # Monitor the folder indefinitely
    while True:
        # List all files in the folder
        files = os.listdir(folder_path)
        
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(folder_path, file)
                
                # Check if the file has not been processed yet
                if not os.path.exists(file_path + "_processed"):
                    print(f"Processing file: {file}")
                    with open(file_path, 'r') as json_file:
                        json_data = json.load(json_file)
                    
                    save_to_hdfs(json_data, file, hdfs_path)
                    
                    # Mark the file as processed
                    open(file_path + "_processed", 'w').close()
                    print(f"File {file} processed and saved to HDFS")

        # Sleep for a while before checking the folder again
        time.sleep(10)

if __name__ == '__main__':

    folder_path = '../../ing_data'

    monitor_folder_and_save_to_hdfs(folder_path)
