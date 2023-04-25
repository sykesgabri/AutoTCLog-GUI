# AutoTCLog-GUI
A version of [AutoTCLog](https://github.com/sykesgabri/AutoTCLog) with a GUI interface. Writing timecode logs manually is tedious and time consuming. AutoTCLog-GUI gets the worst of it done fast so you only have to fill in the easy parts.

This is a GUI program, if you want a CLI version, check out [AutoTCLog](https://github.com/sykesgabri/AutoTCLog)

# IMPORTANT: This code is still very unfinished and has some bugs that AutoTCLog does not have.

Known bugs:
* On Windows, file paths are displayed in the output file with a combination of back and forward slashes. The program still works regardless, but it's a bit annoying.

## Dependencies
* Python3
* Pandas (install with `pip install pandas`)
* OpenPyXL (install with `pip install openpyxl`)
* FFmpeg

## Installing FFmpeg
AutoTCLog-GUI uses FFmpeg to extract video metadata. FFmpeg must be installed on your computer for the program to work. Here's how to install FFmpeg on Windows, MacOS, or Linux:

Windows:
* Download the FFmpeg Windows binary from https://ffmpeg.org/download.html#build-windows
* Extract the downloaded archive to a folder of your choice
* Add the FFmpeg executable to your system's PATH environment variable

MacOS:
* Install Homebrew from https://brew.sh/
* Open a terminal and run the following command: `brew install ffmpeg`

Linux:
* Use your distro's package manager to install the `ffmpeg` package

## Using AutoTCLog-GUI
1. Clone this repository to your computer by opening a terminal and typing `git clone https://github.com/sykesgabri/AutoTCLog-GUI`. Alternatively, you can click the green "Code" button on this repository, click "Download ZIP", then extract the ZIP file
2. Open a terminal and navigate to the AutoTCLog-GUI folder
3. Type the command `python3 autotclog-GUI.py`
4. Follow the instructions provided to you by the program

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
