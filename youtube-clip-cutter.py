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

# Cleanup function to delete old files
def cleanup_old_files():
    while True:
        time.sleep(600)  # Sleep for 10 minutes
        folder_path = "downloads"
        current_time = time.time()
        
        # Delete files older than 10 minutes
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 600:  # 600 seconds = 10 minutes
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")

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

        # Single slider for selecting a region in the video (in seconds)
        region = st.slider(
            "Select Trim Region (Start and End)", 
            0, video_duration, 
            (0, video_duration), 1,  # Step is set to 1
            key="trim_region_slider"  # Unique key for the slider
        )

        start_time = region[0]
        end_time = region[1]

        # Display the selected start and end times in MM:SS format
        st.write(f"Start Time: {seconds_to_mmss(start_time)}")
        st.write(f"End Time: {seconds_to_mmss(end_time)}")

        # Download button
        if st.button("Start Trimming"):
            if not st.session_state.download_started:
                file_path = download_video(url)
                st.session_state['downloaded_file'] = file_path
            else:
                st.write(f"Video is already downloading or downloaded.")

            # Trim the video based on user input times
            if st.session_state.downloaded_file:
                trimmed_file = trim_video(st.session_state['downloaded_file'], start_time, end_time)
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
