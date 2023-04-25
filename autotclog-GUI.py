import os
import glob
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# function to display warning about videos with different framerates
def show_framerate_warning():
    messagebox.showwarning('Warning', 'It is advised to keep video files with different framerates in separate folders for this program to work best.')

# function to get video metadata
def get_metadata(path):
    # scan for video files
    video_files = glob.glob(os.path.join(path, '*.mp4')) + \
                  glob.glob(os.path.join(path, '*.avi')) + \
                  glob.glob(os.path.join(path, '*.mov')) + \
                  glob.glob(os.path.join(path, '*.mts'))

    metadata = []
    framerates = set()
    for file in video_files:
        # get video metadata
        fps_string = os.popen(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate {file}').read().strip()
        fps_parts = fps_string.split('/')
        if len(fps_parts) == 2:
            fps = float(fps_parts[0]) / float(fps_parts[1])
        else:
            fps = float(fps_string)
        duration = float(os.popen(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=duration {file}').read())
        metadata.append({
            'file': file,
            'fps': fps,
            'duration': duration
        })
        framerates.add(fps)

    # check for multiple framerates
    if len(framerates) > 1:
        show_framerate_warning()

    return metadata

# function to convert timecode string to frame number
def timecode_to_frame(timecode, fps):
    if not timecode:
        timecode = '00:00:00:00'
    h, m, s, f = map(int, timecode.split(':'))
    return (h * 3600 + m * 60 + s) * fps + f

# function to convert frame number to timecode string
def frame_to_timecode(frame, fps):
    total_seconds = int(frame // fps)
    h, m, s = total_seconds // 3600, (total_seconds // 60) % 60, total_seconds % 60
    f = int(frame % fps)
    return f'{h:02d}:{m:02d}:{s:02d}:{f:02d}'

# function to handle browse button click
def browse_path():
    folder_path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_path)

# function to handle start timecode entry
def validate_timecode():
    timecode = timecode_entry.get()
    if len(timecode) != 11:
        messagebox.showerror('Error', 'Invalid timecode format. Please enter timecode as HH:MM:SS:FF.')
        return False
    for t in timecode.split(':'):
        if not t.isdigit():
            messagebox.showerror('Error', 'Invalid timecode format. Please enter timecode as HH:MM:SS:FF.')
            return False
    return True

# function to handle browse output path button click
def browse_output_path():
    output_path = filedialog.askdirectory()
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, output_path)

# function to handle run button click
def run():
    # get input values from GUI
    path = path_entry.get()
    start_timecode = timecode_entry.get()
    output_path = output_path_entry.get()
    output_file = output_file_entry.get()

    # check if output file name is empty and set default value
    if not output_file:
        output_file = 'AutoTCLog'

    # get video metadata
    metadata = get_metadata(path)

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
            if not start_timecode:
                start_timecode = '00:00:00:00'
            timecode_in = start_timecode
        else:
            timecode_in = df.loc[i-1, 'Timecode Out']
        frame_in = timecode_to_frame(timecode_in, fps)
        frame_out = frame_in + duration * fps
        timecode_out = frame_to_timecode(frame_out, fps)

        # add row to dataframe
        file_name, file_ext = os.path.splitext(os.path.basename(file))
        file_path = os.path.join(output_path, file_name + file_ext)
        df.loc[i] = [file_path, timecode_in, timecode_out, '', '', '']

    # save dataframe to excel file
    file_path = os.path.join(output_path, output_file + '.xlsx')
    df.to_excel(file_path, index=False)

    messagebox.showinfo('Info', f"Output file saved to {file_path}")

# create GUI
root = tk.Tk()
root.title('AutoTCLog-GUI')

# create frame for folder path input
path_frame = tk.Frame(root)
path_frame.pack(fill=tk.X, padx=10, pady=10)
path_label = tk.Label(path_frame, text='Folder Path:')
path_label.pack(side=tk.LEFT)
path_entry = tk.Entry(path_frame)
path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
path_button = tk.Button(path_frame, text='Browse', command=browse_path)
path_button.pack(side=tk.LEFT)

# create frame for start timecode input
timecode_frame = tk.Frame(root)
timecode_frame.pack(fill=tk.X, padx=10, pady=10)
timecode_label = tk.Label(timecode_frame, text='Start Timecode:')
timecode_label.pack(side=tk.LEFT)
timecode_entry = tk.Entry(timecode_frame, width=11)
timecode_entry.pack(side=tk.LEFT)
default_timecode_label = tk.Label(timecode_frame, text='(default: 00:00:00:00)')
default_timecode_label.pack(side=tk.LEFT)

#create frame for output file path input
output_path_frame = tk.Frame(root)
output_path_frame.pack(fill=tk.X, padx=10, pady=10)
output_path_label = tk.Label(output_path_frame, text='Output File Path:')
output_path_label.pack(side=tk.LEFT)
output_path_entry = tk.Entry(output_path_frame)
output_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
output_path_button = tk.Button(output_path_frame, text='Browse', command=browse_output_path)
output_path_button.pack(side=tk.LEFT)

# create frame for output file name input
output_file_frame = tk.Frame(root)
output_file_frame.pack(fill=tk.X, padx=10, pady=10)
output_file_label = tk.Label(output_file_frame, text='Output File Name:')
output_file_label.pack(side=tk.LEFT)
output_file_entry = tk.Entry(output_file_frame)
output_file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

# create run button
run_button = tk.Button(root, text='Run', command=run)
run_button.pack(pady=10)

root.mainloop()