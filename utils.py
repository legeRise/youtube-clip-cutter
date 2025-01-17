import os
import time


# Function to convert mm:ss to total seconds
def convert_to_seconds(minutes, seconds):
    return minutes * 60 + seconds

# Function to convert seconds into MM:SS format
def seconds_to_mmss(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


# Function to format duration
def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"

def cleanup_old_files(instant=False):
    folder_path = "downloads"
    sleep_interval = 600  # 10 minutes
    max_file_age = 1200  # 20 minutes

    while True:
        if not instant:
            time.sleep(sleep_interval)

        if not os.path.exists(folder_path):
            continue  # Skip if the folder doesn't exist

        current_time = time.time()

        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file():
                    file_path = entry.path
                    file_age = current_time - entry.stat().st_mtime
                    if file_age > max_file_age:
                        try:
                            os.remove(file_path)
                            print(f"Deleted old file: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")