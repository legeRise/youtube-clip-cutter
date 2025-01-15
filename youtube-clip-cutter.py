# import streamlit as st
# import yt_dlp as ytdlp
# import os
# import time
# import threading

# # Function to download video using yt-dlp
# def download_video(url):
#     st.session_state['download_started'] = True
#     ydl_opts = {
#         'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
#         'outtmpl': 'downloads/%(id)s.%(ext)s',
#         'noplaylist': True,
#         'quiet': False,
#         'merge_output_format': 'mp4',  # Force merge to MP4
#         'progress_hooks': [progress_hook],
#     }

#     with ytdlp.YoutubeDL(ydl_opts) as ydl:
#         info_dict = ydl.extract_info(url, download=False)
#         video_url = info_dict.get("url", None)
#         video_ext = info_dict.get("ext", "mp4")

#         # Download the video with progress hook
#         st.write("Downloading...")
#         ydl.download([url])

#     st.session_state['downloaded_file'] = f'downloads/{info_dict["id"]}.{video_ext}'
#     return st.session_state['downloaded_file']

# # Function for the progress hook during download
# def progress_hook(d):
#     if d['status'] == 'downloading':
#         # Update the progress in session state
#         st.session_state['download_progress'] = d['downloaded_bytes'] / d['total_bytes']
#         # Update the progress bar in the session state
#         st.session_state['download_progress_bar'].progress(st.session_state['download_progress'])

# # Function to trim the video (re-encoding with ffmpeg for compatibility)
# def trim_video(input_file, start_time, end_time):
#     trimmed_file = f"downloads/trimmed_{start_time}-{end_time}.mp4"
#     # Re-encode the video to ensure compatibility
#     command = f"ffmpeg -i {input_file} -ss {start_time} -to {end_time} -c:v libx264 -c:a aac -strict experimental {trimmed_file}"
#     os.system(command)
#     return trimmed_file

# # Function to convert seconds into MM:SS format
# def seconds_to_mmss(seconds):
#     minutes = seconds // 60
#     seconds = seconds % 60
#     return f"{minutes:02}:{seconds:02}"

# # Function to convert mm:ss to total seconds
# def convert_to_seconds(minutes, seconds):
#     return minutes * 60 + seconds

# # Function to format duration
# def format_duration(seconds):
#     hours = seconds // 3600
#     minutes = (seconds % 3600) // 60
#     seconds = seconds % 60
#     if hours > 0:
#         return f"{hours:02}:{minutes:02}:{seconds:02}"
#     else:
#         return f"{minutes:02}:{seconds:02}"

# # Cleanup function to delete old files
# def cleanup_old_files():
#     while True:
#         time.sleep(600)  # Sleep for 10 minutes
#         folder_path = "downloads"
#         current_time = time.time()

#         # Delete files older than 10 minutes
#         for filename in os.listdir(folder_path):
#             file_path = os.path.join(folder_path, filename)
#             file_age = current_time - os.path.getmtime(file_path)
#             if file_age > 600:  # 600 seconds = 10 minutes
#                 os.remove(file_path)
#                 print(f"Deleted old file: {file_path}")

# # Start cleanup in a separate thread
# cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
# cleanup_thread.start()

# def main():
#     # Set page configuration
#     st.set_page_config(page_title="YouTube Clip Cutter", layout="centered")

#     st.title("YouTube Clip Cutter")

#     # Session state initialization
#     if "download_started" not in st.session_state:
#         st.session_state.download_started = False
#     if "downloaded_file" not in st.session_state:
#         st.session_state.downloaded_file = None
#     if "download_progress" not in st.session_state:
#         st.session_state['download_progress'] = 0.0
#     if "download_progress_bar" not in st.session_state:
#         st.session_state['download_progress_bar'] = st.progress(0)  # Initialize the progress bar

#     # Input for YouTube video link
#     url = st.text_input("Enter YouTube Video URL:")

#     if url:
#         # Get video info using yt-dlp
#         ydl_opts = {
#             'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
#             'outtmpl': 'downloads/%(id)s.%(ext)s',
#             'noplaylist': True,
#             'quiet': True,
#         }

#         with ytdlp.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(url, download=False)
#             title = info_dict.get('title', 'No Title Available')
#             video_duration = info_dict.get('duration', 0)  # Video duration in seconds
#             st.write(f"Video Title: {title}")
#             st.write(f"Video Duration: {video_duration // 60} minutes {video_duration % 60} seconds")

#         # Initialize session state for start and end times
#         if 'start_time' not in st.session_state:
#             st.session_state.start_time = 0
#         if 'end_time' not in st.session_state:
#             st.session_state.end_time = video_duration

#         # Create a form for input fields
#         with st.form(key='time_input_form'):
#             st.write("Start time:")
#             start_col1, start_col2 = st.columns(2)
#             with start_col1:
#                 start_minutes = st.number_input(
#                     "Minutes",
#                     min_value=0,
#                     max_value=video_duration // 60,  # Maximum minutes based on video duration
#                     value=st.session_state.start_time // 60,
#                     step=1,
#                     key='fine_start_minutes_input'
#                 )
#             with start_col2:
#                 start_seconds = st.number_input(
#                     "Seconds",
#                     min_value=0,
#                     max_value=59,
#                     value=st.session_state.start_time % 60,
#                     step=1,
#                     key='fine_start_seconds_input'
#                 )

#             st.write("End time:")
#             end_col1, end_col2 = st.columns(2)
#             with end_col1:
#                 end_minutes = st.number_input(
#                     "Minutes",
#                     min_value=0,
#                     max_value=(video_duration // 60),  # Maximum minutes based on video duration
#                     value=min(st.session_state.end_time // 60, video_duration // 60),
#                     step=1,
#                     key='fine_end_minutes_input'
#                 )
#             with end_col2:
#                 max_end_seconds = 59 if (end_minutes * 60 + 59) <= video_duration else (video_duration % 60)
#                 end_seconds = st.number_input(
#                     "Seconds",
#                     min_value=0,
#                     max_value=max_end_seconds,
#                     value=min(st.session_state.end_time % 60, max_end_seconds),
#                     step=1,
#                     key='fine_end_seconds_input'
#                 )

#             submit_button = st.form_submit_button(label='Set')

#         if submit_button:
#             st.session_state.start_time = convert_to_seconds(start_minutes, start_seconds)
#             st.session_state.end_time = convert_to_seconds(end_minutes, end_seconds)

#             # Ensure start time is less than or equal to end time
#             if st.session_state.start_time >= st.session_state.end_time:
#                 st.error("Start time must be less than end time.")
#             else:
#                 # Convert the selected start and end times to mm:ss format
#                 start_time_mm_ss = seconds_to_mmss(st.session_state.start_time)
#                 end_time_mm_ss = seconds_to_mmss(st.session_state.end_time)

#                 # Display the selected start and end times in MM:SS format
#                 st.write(f"Start Time: {start_time_mm_ss}")
#                 st.write(f"End Time: {end_time_mm_ss}")

#                 # Calculate the clip duration in seconds
#                 clip_duration = st.session_state.end_time - st.session_state.start_time

#                 # Display the clip duration
#                 st.write(f"Clip Duration: {format_duration(clip_duration)}")

#         # Download button
#         if st.button("Start Trimming"):
#             if not st.session_state.download_started:
#                 file_path = download_video(url)
#                 st.session_state['downloaded_file'] = file_path
#             else:
#                 st.write(f"Video is already downloading or downloaded.")

#             # Trim the video based on user input times
#             if st.session_state.downloaded_file:
#                 trimmed_file = trim_video(st.session_state['downloaded_file'], st.session_state.start_time, st.session_state.end_time)
#                 st.write(f"Trimmed video is ready for download!")

#                 # Show a download link for the trimmed video
#                 with open(trimmed_file, "rb") as f:
#                     st.download_button("Download Trimmed Video", f, file_name=trimmed_file)

#                 # Display the trimmed video within the app
#                 st.video(trimmed_file)  # Play the trimmed video directly in the app

#     else:
#         st.warning("Please enter a valid YouTube URL.")

# if __name__ == "__main__":
#     main()


#___________________________________________________________________________________


import streamlit as st
import yt_dlp as ytdlp
import os
import time
import threading

# Function to download video using yt-dlp
def download_video(url):
    st.session_state['download_started'] = True
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'merge_output_format': 'mp4',  # Force merge to MP4
        'progress_hooks': [progress_hook],
    }

    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict.get("url", None)
        video_ext = info_dict.get("ext", "mp4")

        # Download the video with progress hook
        st.write("Downloading...")
        ydl.download([url])

    st.session_state['downloaded_file'] = f'downloads/{info_dict["id"]}.{video_ext}'
    return st.session_state['downloaded_file']

# Function for the progress hook during download
def progress_hook(d):
    if d['status'] == 'downloading':
        # Update the progress in session state
        st.session_state['download_progress'] = d['downloaded_bytes'] / d['total_bytes']
        # Update the progress bar in the session state
        st.session_state['download_progress_bar'].progress(st.session_state['download_progress'])

# Function to trim the video (re-encoding with ffmpeg for compatibility)
def trim_video(input_file, start_time, end_time):
    trimmed_file = f"downloads/trimmed_{start_time}-{end_time}.mp4"
    # Re-encode the video to ensure compatibility
    command = f"ffmpeg -i {input_file} -ss {start_time} -to {end_time} -c:v libx264 -c:a aac -strict experimental {trimmed_file}"
    os.system(command)
    return trimmed_file

# Function to convert seconds into MM:SS format
def seconds_to_mmss(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

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

# Cleanup function to delete old files
def cleanup_old_files():
    file_creation_times = {}
    folder_path = "downloads"

    while True:
        time.sleep(60)  # Sleep for 1 minute
        current_time = time.time()

        # Check for new files and update their creation times
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename not in file_creation_times:
                file_creation_times[filename] = os.path.getmtime(file_path)

        # Delete files older than 20 minutes
        for filename, creation_time in list(file_creation_times.items()):
            file_age = current_time - creation_time
            if file_age > 1200:  # 1200 seconds = 20 minutes
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")
                del file_creation_times[filename]

# Start cleanup in a separate thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

def main():
    # Set page configuration
    st.set_page_config(page_title="YouTube Clip Cutter", layout="centered")

    st.title("YouTube Clip Cutter")

    # Session state initialization
    if "download_started" not in st.session_state:
        st.session_state.download_started = False
    if "downloaded_file" not in st.session_state:
        st.session_state.downloaded_file = None
    if "download_progress" not in st.session_state:
        st.session_state['download_progress'] = 0.0
    if "download_progress_bar" not in st.session_state:
        st.session_state['download_progress_bar'] = st.progress(0)  # Initialize the progress bar

    # Input for YouTube video link
    url = st.text_input("Enter YouTube Video URL:")

    if url:
        # Get video info using yt-dlp
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        with ytdlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'No Title Available')
            video_duration = info_dict.get('duration', 0)  # Video duration in seconds
            st.write(f"Video Title: {title}")
            st.write(f"Video Duration: {video_duration // 60} minutes {video_duration % 60} seconds")

        # Initialize session state for start and end times
        if 'start_time' not in st.session_state:
            st.session_state.start_time = 0
        if 'end_time' not in st.session_state:
            st.session_state.end_time = video_duration

        # Create a form for input fields
        with st.form(key='time_input_form'):
            st.write("Start time:")
            start_col1, start_col2 = st.columns(2)
            with start_col1:
                start_minutes = st.number_input(
                    "Minutes",
                    min_value=0,
                    max_value=video_duration // 60,  # Maximum minutes based on video duration
                    value=st.session_state.start_time // 60,
                    step=1,
                    key='fine_start_minutes_input'
                )
            with start_col2:
                start_seconds = st.number_input(
                    "Seconds",
                    min_value=0,
                    max_value=59,
                    value=st.session_state.start_time % 60,
                    step=1,
                    key='fine_start_seconds_input'
                )

            st.write("End time:")
            end_col1, end_col2 = st.columns(2)
            with end_col1:
                end_minutes = st.number_input(
                    "Minutes",
                    min_value=0,
                    max_value=(video_duration // 60),  # Maximum minutes based on video duration
                    value=min(st.session_state.end_time // 60, video_duration // 60),
                    step=1,
                    key='fine_end_minutes_input'
                )
            with end_col2:
                max_end_seconds = 59 if (end_minutes * 60 + 59) <= video_duration else (video_duration % 60)
                end_seconds = st.number_input(
                    "Seconds",
                    min_value=0,
                    max_value=max_end_seconds,
                    value=min(st.session_state.end_time % 60, max_end_seconds),
                    step=1,
                    key='fine_end_seconds_input'
                )

            submit_button = st.form_submit_button(label='Set')

        if submit_button:
            st.session_state.start_time = convert_to_seconds(start_minutes, start_seconds)
            st.session_state.end_time = convert_to_seconds(end_minutes, end_seconds)

            # Ensure start time is less than or equal to end time
            if st.session_state.start_time >= st.session_state.end_time:
                st.error("Start time must be less than end time.")
            else:
                # Convert the selected start and end times to mm:ss format
                start_time_mm_ss = seconds_to_mmss(st.session_state.start_time)
                end_time_mm_ss = seconds_to_mmss(st.session_state.end_time)

                # Display the selected start and end times in MM:SS format
                st.write(f"Start Time: {start_time_mm_ss}")
                st.write(f"End Time: {end_time_mm_ss}")

                # Calculate the clip duration in seconds
                clip_duration = st.session_state.end_time - st.session_state.start_time

                # Display the clip duration
                st.write(f"Clip Duration: {format_duration(clip_duration)}")

        # Download button
        if st.button("Start Trimming"):
            if not st.session_state.download_started:
                file_path = download_video(url)
                st.session_state['downloaded_file'] = file_path
            else:
                st.write(f"Video is already downloading or downloaded.")

            # Trim the video based on user input times
            if st.session_state.downloaded_file:
                trimmed_file = trim_video(st.session_state['downloaded_file'], st.session_state.start_time, st.session_state.end_time)
                st.write(f"Trimmed video is ready for download!")

                # Show a download link for the trimmed video
                with open(trimmed_file, "rb") as f:
                    st.download_button("Download Trimmed Video", f, file_name=trimmed_file)

                # Display the trimmed video within the app
                st.video(trimmed_file)  # Play the trimmed video directly in the app

    else:
        st.warning("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()
