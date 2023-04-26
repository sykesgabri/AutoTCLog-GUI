import os
import glob
import pandas as pd
import colorama
from colorama import Fore, Back, Style
import tkinter as tk
from tkinter import filedialog

# display ascii art logo
with open('logo.txt', 'r', encoding='utf-8') as file:
    art = file.read()
print(Fore.MAGENTA + art)
print(Style.RESET_ALL + 'Version 1.0.1\n')

# function to get video metadata
def get_metadata(path):
    # scan for video files
    video_files = glob.glob(os.path.join(path, '*.mp4')) + \
                  glob.glob(os.path.join(path, '*.avi')) + \
                  glob.glob(os.path.join(path, '*.mov')) + \
                  glob.glob(os.path.join(path, '*.mpg'))

    metadata = []
    framerates = []
    for file in video_files:
        # get video metadata
        fps_string = os.popen(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "{file}"').read().strip()
        fps_parts = fps_string.split('/')
        if len(fps_parts) == 2:
            fps = float(fps_parts[0]) / float(fps_parts[1])
        else:
            if '\n' in fps_string:
                fps_list = []
                for x in fps_string.split('\n'):
                    x = x.strip()
                    try:
                        fps_list.append(float(x))
                    except ValueError:
                        print(f"Error: could not convert '{x}' to float for file '{file}'")
                if len(fps_list) == 0:
                    fps = None
                elif len(fps_list) == 1:
                    fps = fps_list[0]
                else:
                    fps = sum(fps_list) / len(fps_list)
            else:
                try:
                    fps = float(fps_string)
                except ValueError:
                    print(f"Error: could not convert '{fps_string}' to float for file '{file}'")
                    fps = None
        duration_string = os.popen(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=duration "{file}"').read()
        try:
            duration = float(duration_string.strip())
        except ValueError:
            duration_parts = duration_string.strip().split('\n')
            duration_list = [float(x) for x in duration_parts if x.strip()]
            if len(duration_list) == 0:
                duration = None
            elif len(duration_list) == 1:
                duration = duration_list[0]
            else:
                duration = sum(duration_list) / len(duration_list)
            if duration is None:
                print(f"Error: could not convert '{duration_string}' to float for file '{file}'")
        
        if fps is not None and duration is not None:
            metadata.append({
                'file': file,
                'fps': fps,
                'duration': duration
            })
            framerates.append(fps)

    # check for multiple framerates
    if len(set(framerates)) > 1:
        print("Note: It is advised to keep video files with different framerates in separate folders for this program to work best.")

    return metadata

# function to convert timecode string to frame number
def timecode_to_frame(timecode, fps):
    h, m, s, f = map(int, timecode.split(':'))
    return (h * 3600 + m * 60 + s) * fps + f

# function to convert frame number to timecode string
def frame_to_timecode(frame, fps):
    total_seconds = int(frame // fps)
    h, m, s = total_seconds // 3600, (total_seconds // 60) % 60, total_seconds % 60
    f = int(frame % fps)
    return f'{h:02d}:{m:02d}:{s:02d}:{f:02d}'

# function to browse for input folder path
def browse_input_folder():
    global input_folder_path
    input_folder_path = filedialog.askdirectory()
    input_folder_path_text.delete(0, tk.END)
    input_folder_path_text.insert(0, input_folder_path)

# function to browse for output folder path
def browse_output_folder():
    global output_folder_path
    output_folder_path = filedialog.askdirectory()
    output_folder_path_text.delete(0, tk.END)
    output_folder_path_text.insert(0, output_folder_path)

# function to start processing
def start_processing():
    # get folder path from user input
    path = input_folder_path
    print("Scanning folder, please wait...")

    # get video metadata
    metadata = get_metadata(path)

    # get start timecode from user input
    start_timecode = start_timecode_text.get()

    # check if start timecode is empty and set default value
    if not start_timecode:
        start_timecode = '00:00:00:00'

    # ask user for output file name and location
    output_path = output_folder_path_text.get()
    output_file = output_file_text.get()

    # create pandas dataframe to store results
    df = pd.DataFrame(columns=['File', 'Timecode In', 'Timecode Out', 'Scene Number', 'Shot Number', 'Usable'])

    # process each video file
    for i, file_metadata in enumerate(metadata):
        # get file name and metadata
        file = file_metadata['file']
        fps = file_metadata['fps']
        duration = file_metadata['duration']

        # calculate timecode in and timecode out
        if i == 0:
            timecode_in = start_timecode
        else:
            timecode_in = df.loc[i-1, 'Timecode Out']
        frame_in = timecode_to_frame(timecode_in, fps)
        frame_out = frame_in + duration * fps
        timecode_out = frame_to_timecode(frame_out, fps)

        # add row to dataframe
        if output_path:
            file_name = os.path.splitext(os.path.basename(file))[0] + os.path.splitext(file)[-1]
            file_name_no_ext = os.path.splitext(os.path.basename(file))[0]
            file_path = os.path.join(output_path, f'{os.path.splitext(os.path.basename(file))[0]}{os.path.splitext(file)[-1]}')
        else:
            file_path = os.path.splitext(file)[0] + '.xlsx'
        df.loc[i] = [file_path, timecode_in, timecode_out, '', '', '']

    # save dataframe to excel file
    if output_path:
        file_path = os.path.join(output_path, f'{output_file}.xlsx')
    else:
        file_path = os.path.join(path, f'{output_file}.xlsx')
    df.to_excel(file_path, index=False)

    print(f"Output file saved to {file_path}")

# create GUI window
root = tk.Tk()
root.title("Video Scene Detection Tool")

# create input folder path label and textbox
input_folder_path_label = tk.Label(root, text="Input folder path:")
input_folder_path_label.grid(row=0, column=0)
input_folder_path_text = tk.Entry(root)
input_folder_path_text.grid(row=0, column=1)
browse_input_folder_button = tk.Button(root, text="Browse", command=browse_input_folder)
browse_input_folder_button.grid(row=0, column=2)

# create start timecode label and textbox
start_timecode_label = tk.Label(root, text="Start timecode (HH:MM:SS:FF):")
start_timecode_label.grid(row=1, column=0)
start_timecode_text = tk.Entry(root)
start_timecode_text.grid(row=1, column=1)

# create output folder path label and textbox
output_folder_path_label = tk.Label(root, text="Output folder path:")
output_folder_path_label.grid(row=2, column=0)
output_folder_path_text = tk.Entry(root)
output_folder_path_text.grid(row=2, column=1)
browse_output_folder_button = tk.Button(root, text="Browse", command=browse_output_folder)
browse_output_folder_button.grid(row=2, column=2)

# create output file name label and textbox
output_file_label = tk.Label(root, text="Output file name (excluding file extension):")
output_file_label.grid(row=3, column=0)
output_file_text = tk.Entry(root)
output_file_text.grid(row=3, column=1)

# create start processing button
start_processing_button = tk.Button(root, text="Start Processing", command=start_processing)
start_processing_button.grid(row=4, column=1)

# start GUI event loop
root.mainloop()
