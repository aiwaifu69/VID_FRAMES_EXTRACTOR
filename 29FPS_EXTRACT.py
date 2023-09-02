import cv2
import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import threading

# Function to sanitize a file name
def sanitize_filename(filename):
    # Define a mapping of special characters to replacement strings
    special_chars = {
        "<": "",
        ">": "",
        ":": "",
        "\"": "",
        "/": "",
        "\\": "",
        "|": "",
        "?": "",
        "*": "",
    }

    # Replace each special character in the file name
    for char, replacement in special_chars.items():
        filename = filename.replace(char, replacement)

    return filename

# Function to process a frame
def process_frame(frame_file, frame):
    if not os.path.isfile(frame_file):
        cv2.imwrite(frame_file, frame)

# Create a Tkinter root widget
root = tk.Tk()
root.withdraw()  # Hide the root widget

# Open a file dialog for the user to choose the video files
video_files = filedialog.askopenfilenames(title="Choose video files", filetypes=[("Video files", "*.mp4;*.ts;*.mkv;*.avi;*.mov")])

# Check if the user canceled the file dialog
if not video_files:
    print("No video files chosen, exiting.")
    exit()

# Set the default output directory
base_output_dir = filedialog.askdirectory(title="Choose output directory")

# Create a ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10)

# Initialize a counter for the current video
current_video = 0

# Initialize a counter for the total frames
total_frames_extracted = 0

# Store the start time
start_time = time.time()

# Loop over the video files
for video_file in video_files:
    try:
        # Load the video
        cap = cv2.VideoCapture(video_file)

        # Get the frames per second (fps) of the video
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Define the frame extraction rate (every 30 frames)
        frame_rate = 29

        # Get the base name of the video file without the extension
        base_name = os.path.splitext(os.path.basename(video_file))[0]

        # Create a directory for the current video file
        output_dir = os.path.join(base_output_dir, base_name)
        os.makedirs(output_dir, exist_ok=True)

        # Initialize a counter for the current frame
        current_frame = 0

        # Get total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Loop over all frames in the video
        while True:
            # Read the current frame
            is_read, frame = cap.read()

            # Check if the frame was read correctly
            if not is_read:
                break

            # Check if the current frame number is divisible by the frame rate
            if current_frame % frame_rate == 0:
                # Define the output frame file name
                frame_file = os.path.join(output_dir, f"{sanitize_filename(base_name)}_{current_frame // frame_rate}.png")

                # Process the frame in a separate thread
                executor.submit(process_frame, frame_file, frame)
                total_frames_extracted += 1

            # Increment the current frame number
            current_frame += 1

        # Release the video file
        cap.release()

        print(f"Frames for {base_name} have been extracted to the directory: {output_dir}")

        # Increment the current video number
        current_video += 1

        # Calculate the progress percentage and ETA
        progress_percentage = (current_video / len(video_files)) * 100
        elapsed_time = time.time() - start_time
        eta = elapsed_time * (100 - progress_percentage) / progress_percentage

        # Print the progress status
        print(f"Total video files: {len(video_files)}, Total Frames extracted: {progress_percentage:.2f}%, ETA: {eta/60:.2f} mins remaining")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing {video_file}: {str(e)}")

messagebox.showinfo("Information", "All video files processed.")
