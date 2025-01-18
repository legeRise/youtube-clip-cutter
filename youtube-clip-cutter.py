import streamlit as st
import os
import logging
from yt_clipper import YTClipper
from utils import *

# Set up logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Set page configuration
st.set_page_config(page_title="YouTube Clip Cutter", layout="centered")

# Create an instance of the YouTube clipper
if "yt_clipper" not in st.session_state:
    st.session_state.yt_clipper = YTClipper()

# Initialize session state
if "download_started" not in st.session_state:
    st.session_state.download_started = False
if "downloaded_file" not in st.session_state:
    st.session_state.downloaded_file = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "end_time" not in st.session_state:
    st.session_state.end_time = 0

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
    st.session_state.start_time = 0
    st.session_state.end_time = 0
    st.session_state.video_id = None

if url:
    try:
        # Fetch video metadata using YTClipper
        info_dict = st.session_state.yt_clipper.get_video_metadata(url)
        st.session_state.video_id = info_dict.get("id", "unknown")
        title = info_dict.get('title', 'No Title Available')
        video_duration = info_dict.get('duration', 0)

        # Display video details
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

        # Update session states with selected times
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

        # Trigger video trimming process
        if st.button("Start Trimming"):
            print("trimming button was clicked")
            if not st.session_state.download_started:
                start_time = seconds_to_mmss(st.session_state.start_time)
                end_time = seconds_to_mmss(st.session_state.end_time)

                # Use st.spinner while downloading and trimming
                with st.spinner("Trimming your video... This may take a while."):
                    # Directly use the trimmed file path from yt_clipper
                    trimmed_file_path = st.session_state.yt_clipper.download_and_cut(
                        url, start_time, end_time, output_file="clip.mp4"
                    )
                    print("trimmed_file_path", trimmed_file_path)

                    # Check if trimmed_file_path is returned correctly
                    if isinstance(trimmed_file_path, str) and os.path.exists(trimmed_file_path):
                        st.write("Trimmed video is ready for download!")
                        with open(trimmed_file_path, "rb") as f:
                            st.download_button("Download Trimmed Video", f, file_name=os.path.basename(trimmed_file_path))

                        # Delete the trimmed file after download
                        os.unlink(trimmed_file_path)
                        st.session_state.download_started = False
                    else:
                        st.error("Error: No valid file path returned from yt_clipper.")

        # Resetting session states on "Create New"
        if st.button("Create New"):
            st.session_state.download_started = False
            st.session_state.downloaded_file = None
            st.session_state.start_time = 0
            st.session_state.end_time = 0
            st.session_state.video_id = None
            st.write('<script>window.location.reload();</script>', unsafe_allow_html=True)

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        st.error(f"An unexpected error occurred: {e}")

else:
    st.warning("Please enter a valid YouTube URL.")

