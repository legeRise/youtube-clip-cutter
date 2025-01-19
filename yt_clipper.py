import os
import subprocess
import time
import threading
import logging
from yt_dlp import YoutubeDL

class YTClipper:
    def __init__(self, output_dir="clips", auto_delete_time=20 * 60):  # 20 minutes in seconds
        self.output_dir = output_dir
        self.auto_delete_time = auto_delete_time
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Start cleanup thread
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start a background thread to delete old clips."""
        print(f"Active threads before starting cleanup: {threading.active_count()}")
        thread = threading.Thread(target=self._cleanup_old_files, daemon=True)
        thread.start()

    def _cleanup_old_files(self):
        """Delete files older than the specified auto-delete time."""
        while True:
            current_time = time.time()
            for file_name in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file_name)
                if os.path.isfile(file_path):
                    creation_time = os.path.getctime(file_path)
                    if current_time - creation_time > self.auto_delete_time:
                        os.remove(file_path)
                        logging.info(f"Deleted old clip: {file_path}")
                        print(f"Deleted old clip: {file_path}")
            time.sleep(60)  # Check every minute

    def get_video_metadata(self, video_url):
        """Get metadata for a YouTube video."""
        ydl_opts = {
            'format': 'bestvideo+bestaudio',  # Best quality video and audio
            'noplaylist': True,
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_id = info_dict.get("id", "unknown")
            title = info_dict.get('title', 'No Title Available')
            video_duration = info_dict.get('duration', 0)
            logging.info(f"Video Title: {title}")
            logging.info(f"Video Duration: {video_duration // 60} minutes {video_duration % 60} seconds")
            print(f"Video Title: {title}")
            print(f"Video Duration: {video_duration // 60} minutes {video_duration % 60} seconds")
            return {"video_id": video_id, "title": title, "duration": video_duration}

    def download_video(self, video_url, file_name="temp_video", quality="720"):  # 480p
        """Download a YouTube video using yt-dlp."""
        output_path = os.path.join(self.output_dir, f"{file_name}.mp4")
        print(output_path,'is the output path ext')
        ydl_opts = {
            'format': f'bestvideo[ext=mp4][height<=?{quality}]+bestaudio[ext=m4a]/best[ext={quality}]', # f'bestvideo[height<=?{quality}]+bestaudio/best[height<=?{quality}]',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',  # Use the built-in postprocessor for conversion
                'preferedformat': 'mp4',   # single r in prefered matters
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        logging.info(f"Video downloaded: {file_name}")
        print(f"Video downloaded")


        merged_file = os.path.join(self.output_dir, f"{file_name}.mp4")  
        return merged_file

    def cut_video(self, input_file, start_time, end_time, output_file):
        """Trim a video using FFmpeg."""
        print("inside for cutting")
        output_path = os.path.join(self.output_dir, output_file)
        print(f"input path: {input_file}")
        print(f"output path: {output_path}")
        # If output file already exists, rename it by adding a number (e.g., clip_2.mp4)
        if os.path.exists(output_path):
            base, ext = os.path.splitext(output_file)
            i = 1
            while os.path.exists(os.path.join(self.output_dir, f"{base}_{i}{ext}")):
                i += 1
            output_file = f"{base}_{i}{ext}"
            output_path = os.path.join(self.output_dir, output_file)

        command = [
            "ffmpeg",
            "-i", input_file,       # Input file
            "-ss", start_time,      # Start time (e.g., "00:02:30")
            "-to", end_time,        # End time (e.g., "00:02:40")
            "-c", "copy",           # Copy codecs (faster trimming)
            output_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logging.error(f"FFmpeg error: {result.stderr.decode()}")
            print(f"FFmpeg error: {result.stderr.decode()}")
        else:
            logging.info(f"Clip saved: {output_path}")
            print(f"Clip saved: {output_path}")
        print("the output path of return  was: ",output_path)
        return output_path

    def download_and_cut(self, video_url, start_time, end_time, output_file):
        """Download and trim a YouTube video in one step."""
        logging.info("Downloading video...")
        print("Downloading video...")
        temp_file = self.download_video(video_url)  # Get the merged file path
        print(temp_file,'is the temp file')
        logging.info("Cutting the video...")
        print("Cutting the video...")
        trimmed_file = self.cut_video(temp_file, start_time, end_time, output_file)
        print("after trimming",trimmed_file)
        print("temp file: ",temp_file)
        # Remove the temporary merged file after trimming
        os.remove(temp_file)
        
        logging.info(f"Clip saved at: {trimmed_file}")
        print(f"Clip saved at: {trimmed_file}")
        return trimmed_file


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    tool = YTClipper()

    # Specify the video URL, start, end times, and desired output file name
    video_url = "https://youtu.be/o6Or59KSp8Y?si=XRwcDo9pN0JFMWAt"
    start_time = "00:03:30"
    end_time = "00:03:40"
    output_file = "clip.mp4"

    # Download and trim the clip
    tool.get_video_metadata(video_url)
    tool.download_and_cut(video_url, start_time, end_time, output_file)

