from pytubefix import YouTube
import os
import shutil
import sys

# For extension consistency
EXTENSION = "mp4"

url = input("YouTube URL: ")

# Go in download folder if doesn't exist create new
Downloads_path = "your_folder_path"
os.makedirs(Downloads_path, exist_ok=True)

try:
  yt = YouTube(url)
except:
  print("Error")

# Show the information about the video
print(
    f"Title: {yt.title}\n"
    f"Author: {yt.author}\n"
    f"Streams: {yt.streams.filter(progressive=True, file_extension=EXTENSION)}"
      )


# Ask if continue to download
continue_download = input("Continue to download? [y/n]: ").lower().strip()
continue_download = True if continue_download == "y" else False
if not continue_download:
  sys.exit(1)


# Download and store the path of download for transferrring in downloads folder
initial_video_path = yt.streams.filter(progressive=True, file_extension=EXTENSION).last().download()
print("Downloading...")

# If extension duplicate already exist continue adding 1 at the end of file name
path_exist = os.path.exists(f"{Downloads_path}/{yt.title}.{EXTENSION}")
if path_exist:
  counter = 1

  while path_exist:
    # The intial path where the file is downloaded
    file_parts = initial_video_path.split(".")
    file_name = " ".join(file_parts[:len(file_parts) - 1]).replace(".", "_")
    file_extension = file_parts[len(file_parts) - 1]

    # print(file_name, file_extension)

    new_video_path = f"{file_name}({counter}).{file_extension}"

    # Check if it exist already in download folder creating a duplicate
    exist_download = f"{Downloads_path}/{yt.title}({counter}).{file_extension}"
    path_exist = os.path.exists(exist_download)

    if path_exist:
      counter += 1
      continue

  os.rename(initial_video_path, new_video_path)
  final_video_path = new_video_path

  print("File already exist: ",initial_video_path)
  print("Renamed: ",final_video_path)
  
else:
  final_video_path = initial_video_path

final_path = shutil.move(final_video_path, Downloads_path)
print("Final Path", final_path)
print("Program Done")