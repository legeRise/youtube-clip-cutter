# Function to convert mm:ss to total seconds
def convert_to_seconds(minutes, seconds):
    return minutes * 60 + seconds


# Function to format duration
def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"


if __name__ == '__main__':
    # Testing both functions with the same values
    test_values = [
        59,          # Seconds-only
        75,          # Seconds spilling into minutes
        3599,        # Just below 1 hour
        3600,        # Exactly 1 hour
        3665,        # 1 hour, 1 minute, 5 seconds
        90061        # 25 hours, 1 minute, 1 second
    ]

    print("Testing format duration function:")
    for value in test_values:
        print(f"\nInput seconds: {value}")
        print(f"format_duration: {format_duration(value)}")