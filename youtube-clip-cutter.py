# import streamlit as st
# import yt_dlp as ytdlp
# import os
# import time
# import threading

# # Set page configuration
# st.set_page_config(page_title="YouTube Clip Cutter", layout="centered")

# # Initialize session state
# if "download_started" not in st.session_state:
#     st.session_state.download_started = False
# if "downloaded_file" not in st.session_state:
#     st.session_state.downloaded_file = None
# if "download_progress" not in st.session_state:
#     st.session_state.download_progress = 0.0
# if "download_progress_bar" not in st.session_state:
#     st.session_state.download_progress_bar = st.progress(0)
# if "video_id" not in st.session_state:
#     st.session_state.video_id = None
# if "start_time" not in st.session_state:
#     st.session_state.start_time = 0
# if "end_time" not in st.session_state:
#     st.session_state.end_time = 0

# # Function to download video using yt-dlp
# def download_video(url):
#     st.session_state.download_started = True
#     st.session_state.download_progress_bar = st.progress(0)
#     ydl_opts = {
#         'format': 'bestvideo+bestaudio/best',
#         'outtmpl': 'downloads/%(id)s.%(ext)s',
#         'noplaylist': True,
#         'quiet': False,
#         'merge_output_format': 'mp4',
#         'progress_hooks': [progress_hook],
#     }

#     with ytdlp.YoutubeDL(ydl_opts) as ydl:
#         info_dict = ydl.extract_info(url, download=False)
#         # st.session_state.video_id = info_dict.get("id", "unknown")
#         st.write("Downloading...")
#         ydl.download([url])

#     st.session_state.downloaded_file = f'downloads/{st.session_state.video_id}.{info_dict["ext"]}'
#     return st.session_state.downloaded_file

# # Function for the progress hook during download
# def progress_hook(d):
#     if 'downloaded_bytes' in d and 'total_bytes' in d:
#         if d['total_bytes'] != 0:
#             st.session_state.download_progress = d['downloaded_bytes'] / d['total_bytes']
#         else:
#             st.session_state.download_progress = 0.0
#         st.session_state.download_progress_bar.progress(st.session_state.download_progress)
#     else:
#         st.session_state.download_progress = 0.0
#         st.session_state.download_progress_bar.progress(st.session_state.download_progress)

# # Function to trim the video (re-encoding with ffmpeg for compatibility)
# def trim_video(input_file, start_time, end_time):
#     trimmed_file = f"downloads/trimmed_{st.session_state.video_id}-{start_time}-{end_time}.mp4"
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
#     folder_path = "downloads"
#     while True:
#         time.sleep(600)  # Sleep for 10 minutes
#         if not os.path.exists(folder_path):
#             continue
#         current_time = time.time()
#         for filename in os.listdir(folder_path):
#             file_path = os.path.join(folder_path, filename)
#             file_age = current_time - os.path.getmtime(file_path)
#             if file_age > 1200:  # 1200 seconds = 20 minutes
#                 os.remove(file_path)
#                 print(f"Deleted old file: {file_path}")

# # Start cleanup in a separate thread
# cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
# cleanup_thread.start()

# # Main execution
# st.title("YouTube Clip Cutter")

# # Input for YouTube video link
# url = st.text_input("Enter YouTube Video URL:")

# if url:
#     ydl_opts = {
#         'format': 'bestvideo+bestaudio/best',
#         'outtmpl': 'downloads/%(id)s.%(ext)s',
#         'noplaylist': True,
#         'quiet': True,
#     }

#     with ytdlp.YoutubeDL(ydl_opts) as ydl:
#         info_dict = ydl.extract_info(url, download=False)
#         st.session_state.video_id = info_dict.get("id", "unknown")
#         print(st.session_state.video_id)
#         title = info_dict.get('title', 'No Title Available')
#         video_duration = info_dict.get('duration', 0)
#         st.write(f"Video Title: {title}")
#         st.write(f"Video Duration: {video_duration // 60} minutes {video_duration % 60} seconds")

#     # Create a form for input fields
#     with st.form(key='time_input_form'):
#         st.write("Start time:")
#         start_col1, start_col2 = st.columns(2)
#         with start_col1:
#             start_minutes = st.number_input(
#                 "Minutes",
#                 min_value=0,
#                 max_value=video_duration // 60,
#                 value=st.session_state.start_time // 60,
#                 step=1,
#                 key='fine_start_minutes_input'
#             )
#         with start_col2:
#             start_seconds = st.number_input(
#                 "Seconds",
#                 min_value=0,
#                 max_value=59,
#                 value=st.session_state.start_time % 60,
#                 step=1,
#                 key='fine_start_seconds_input'
#             )

#         st.write("End time:")
#         end_col1, end_col2 = st.columns(2)
#         with end_col1:
#             end_minutes = st.number_input(
#                 "Minutes",
#                 min_value=0,
#                 max_value=video_duration // 60,
#                 value=min(st.session_state.end_time // 60, video_duration // 60),
#                 step=1,
#                 key='fine_end_minutes_input'
#             )
#         with end_col2:
#             max_end_seconds = 59 if (end_minutes * 60 + 59) <= video_duration else (video_duration % 60)
#             end_seconds = st.number_input(
#                 "Seconds",
#                 min_value=0,
#                 max_value=max_end_seconds,
#                 value=min(st.session_state.end_time % 60, max_end_seconds),
#                 step=1,
#                 key='fine_end_seconds_input'
#             )

#         submit_button = st.form_submit_button(label='Set')

#     if submit_button:
#         st.session_state.start_time = convert_to_seconds(start_minutes, start_seconds)
#         st.session_state.end_time = convert_to_seconds(end_minutes, end_seconds)

#         if st.session_state.start_time >= st.session_state.end_time:
#             st.error("Start time must be less than end time.")
#         else:
#             start_time_mm_ss = seconds_to_mmss(st.session_state.start_time)
#             end_time_mm_ss = seconds_to_mmss(st.session_state.end_time)
#             st.write(f"Start Time: {start_time_mm_ss}")
#             st.write(f"End Time: {end_time_mm_ss}")
#             clip_duration = st.session_state.end_time - st.session_state.start_time
#             st.write(f"Clip Duration: {format_duration(clip_duration)}")

#     if st.button("Start Trimming"):
#         if not st.session_state.download_started:
#             file_path = download_video(url)
#             st.session_state.downloaded_file = file_path
#         else:
#             st.write("Video is already downloading or downloaded.")

#         if st.session_state.downloaded_file:
#             trimmed_file = trim_video(st.session_state.downloaded_file, st.session_state.start_time, st.session_state.end_time)
#             st.write("Trimmed video is ready for download!")

#             with open(trimmed_file, "rb") as f:
#                 st.download_button("Download Trimmed Video", f, file_name=os.path.basename(trimmed_file))

#             st.video(trimmed_file)
#             st.session_state.download_started = False

#     if st.button("Create New"):
#         # Reset session state variables
#         st.session_state.download_started = False
#         st.session_state.downloaded_file = None
#         st.session_state.download_progress = 0.0
#         st.session_state.download_progress_bar.empty()
#         st.session_state.video_id = None
#         st.session_state.start_time = 0
#         st.session_state.end_time = 0
#         # Clear the inputs
#         # To refresh the page, we can use JavaScript to reload the window
#         st.write('<script>window.location.reload();</script>', unsafe_allow_html=True)
# else:
#     st.warning("Please enter a valid YouTube URL.")


import streamlit as st
import yt_dlp as ytdlp
import os
import time
import threading

# Set page configuration
st.set_page_config(page_title="YouTube Clip Cutter", layout="centered")

# Initialize session state
if "download_started" not in st.session_state:
    st.session_state.download_started = False
if "downloaded_file" not in st.session_state:
    st.session_state.downloaded_file = None
if "download_progress" not in st.session_state:
    st.session_state.download_progress = 0.0
if "download_progress_bar" not in st.session_state:
    st.session_state.download_progress_bar = st.progress(0)
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "end_time" not in st.session_state:
    st.session_state.end_time = 0

# Function to download video using yt-dlp
def download_video(url):
    st.session_state.download_started = True
    st.session_state.download_progress_bar = st.progress(0)
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
    }

    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        st.session_state.video_id = info_dict.get("id", "unknown")
        st.write("Downloading...")
        ydl.download([url])

    st.session_state.downloaded_file = f'downloads/{st.session_state.video_id}.{info_dict["ext"]}'
    return st.session_state.downloaded_file

# Function for the progress hook during download
def progress_hook(d):
    if 'downloaded_bytes' in d and 'total_bytes' in d:
        if d['total_bytes'] != 0:
            st.session_state.download_progress = d['downloaded_bytes'] / d['total_bytes']
        else:
            st.session_state.download_progress = 0.0
        st.session_state.download_progress_bar.progress(st.session_state.download_progress)
    else:
        st.session_state.download_progress = 0.0
        st.session_state.download_progress_bar.progress(st.session_state.download_progress)

# Function to trim the video (re-encoding with ffmpeg for compatibility)
def trim_video(input_file, start_time, end_time):
    trimmed_file = f"downloads/trimmed_{st.session_state.video_id}-{start_time}-{end_time}.mp4"
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
def cleanup_old_files(instant=False):
    folder_path = "downloads"
    while True:
        if not instant:
            time.sleep(600)  # Sleep for 10 minutes
        if not os.path.exists(folder_path):
            continue
        current_time = time.time()
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 1200:  # 1200 seconds = 20 minutes
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")

# Start cleanup in a separate thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

# Main execution
st.title("YouTube Clip Cutter")

# Input for YouTube video link
url = st.text_input("Enter YouTube Video URL:")

# When a new URL is entered, reset relevant session states
if url != st.session_state.get("previous_url", None):
    # Reset previous session states when a new URL is entered
    st.session_state.previous_url = url
    st.session_state.download_started = False
    st.session_state.downloaded_file = None
    st.session_state.download_progress = 0.0
    st.session_state.download_progress_bar = st.progress(0)
    st.session_state.start_time = 0
    st.session_state.end_time = 0
    st.session_state.video_id = None

if url:
    # Extract video details and reset video-related data
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        st.session_state.video_id = info_dict.get("id", "unknown")
        title = info_dict.get('title', 'No Title Available')
        video_duration = info_dict.get('duration', 0)
        st.write(f"Video Title: {title}")
        st.write(f"Video Duration: {video_duration // 60} minutes {video_duration % 60} seconds")

    # Create a form for input fields
    with st.form(key='time_input_form'):
        st.write("Start time:")
        start_col1, start_col2 = st.columns(2)
        with start_col1:
            start_minutes = st.number_input(
                "Minutes",
                min_value=0,
                max_value=video_duration // 60,
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
                max_value=video_duration // 60,
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

        if st.session_state.start_time >= st.session_state.end_time:
            st.error("Start time must be less than end time.")
        else:
            start_time_mm_ss = seconds_to_mmss(st.session_state.start_time)
            end_time_mm_ss = seconds_to_mmss(st.session_state.end_time)
            st.write(f"Start Time: {start_time_mm_ss}")
            st.write(f"End Time: {end_time_mm_ss}")
            clip_duration = st.session_state.end_time - st.session_state.start_time
            st.write(f"Clip Duration: {format_duration(clip_duration)}")

    if st.button("Start Trimming"):
        if not st.session_state.download_started:
            file_path = download_video(url)
            st.session_state.downloaded_file = file_path
        else:
            st.write("Video is already downloading or downloaded.")

        if st.session_state.downloaded_file:
            trimmed_file = trim_video(st.session_state.downloaded_file, st.session_state.start_time, st.session_state.end_time)
            st.write("Trimmed video is ready for download!")

            with open(trimmed_file, "rb") as f:
                st.download_button("Download Trimmed Video", f, file_name=os.path.basename(trimmed_file))

            st.video(trimmed_file)
            st.session_state.download_started = False

    # Resetting session states on "Create New"
    if st.button("Create New"):
        cleanup_old_files(instant=True)
        st.session_state.download_started = False
        st.session_state.downloaded_file = None
        st.session_state.download_progress = 0.0
        st.session_state.download_progress_bar = st.progress(0)
        st.session_state.start_time = 0
        st.session_state.end_time = 0
        st.session_state.video_id = None
        st.write('<script>window.location.reload();</script>', unsafe_allow_html=True)
else:
    st.warning("Please enter a valid YouTube URL.")
