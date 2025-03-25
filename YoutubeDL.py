from pytubefix import YouTube
import os
import shutil
import sys
import subprocess

def main():
  # Get the YouTube URL from the user
  url = input("YouTube URL: ")

  # Define the download path and create the directory if it doesn't exist
  Downloads_path = "Your/path/to/downloads"
  os.makedirs(Downloads_path, exist_ok=True)
  
  try:
    # Initialize the YouTube object with progress and completion callbacks
    yt_url = YouTube(url, on_progress_callback=progress_func, on_complete_callback=complete_func)
  except:
    print("Error")
    sys.exit(1)  # Exit if there's an error initializing YouTube object
  
  # Get the desired media type from the user
  extension = input("What media type [mp4/mp3]? ")
  # Get the available streams for the selected media type
  quality = available_streams(yt_url, extension)
  # Print video information
  print_info(yt_url, quality, extension)

  # Ask the user if they want to continue with the download
  answer = input("Continue to download? [y/n]: ").lower().strip()
  if answer == 'n':
    print("====Download terminated==== \n ====Program Done====")
    sys.exit(1)

  # Download the selected stream and handle file path conflicts
  initial_path = download(quality, yt_url)
  final_path = path_exist(initial_path, Downloads_path, yt_url, extension)

  # Move the final file to the download directory
  final_path = shutil.move(final_path, Downloads_path)
  print("Final Path:", final_path)
  print("Program Done")


def print_info(url, q, e):
  # Print video information
  print("-" * len(url.title))
  print(f"Title: {url.title}\nAuthor: {url.author}")
  
  if e == "mp4":
    print("Resolution:", q.resolution)
  else:
    print("Abr:", q.abr)
  print("-" * len(url.title))


def download(stream, url):
  # Download the selected stream and return the file path
  path = stream.download()
  if stream.type == "video":
    # Handle video download and merge with audio
    path_parts = path.split("/")
    initial_path = "/".join(path_parts[:len(path_parts) - 1])
    video_path = f"{initial_path}/video.mp4"
    os.rename(path, video_path)

    # Get audio stream and download
    print("Choose audio quality: ")
    audio = available_streams(url, "mp3")
    audio_path = audio.download()
    output_path = f"{initial_path}/{stream.title}.mp4"
    
    # Merge video and audio using ffmpeg
    command = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{output_path}"'
    subprocess.run(command, shell=True)

    # Cleanup temporary files
    os.remove(video_path)
    os.remove(audio_path)
    path = output_path

  return path


def path_exist(initial_path, download_path, video, extension):
  # Check if the file already exists in the download directory
  print("-" * len(initial_path))
  path_exist = os.path.exists(f"{download_path}/{video.title}.{extension}")
  if path_exist:
    counter = 1
    while path_exist:
      # Generate a new file name if a duplicate exists
      file_parts = initial_path.split(".")
      file_name = ".".join(file_parts[:len(file_parts) - 1])
      file_extension = file_parts[len(file_parts) - 1]

      new_video_path = f"{file_name}({counter}).{file_extension}"
      exist_download = f"{download_path}/{video.title}({counter}).{file_extension}"
      path_exist = os.path.exists(exist_download)

      if path_exist:
        counter += 1
        continue

      os.rename(initial_path, new_video_path)
      print("File already exists: ", initial_path)
      print("Renamed: ", new_video_path)
      print("-" * len(new_video_path))
      return new_video_path
    
  else:
    print("-" * len(initial_path))
    return initial_path


def available_streams(stream, file_extension):
  # Get available streams for the selected file extension
  seen_quality = {}
  print("Available qualities: ")
  if file_extension == "mp4":
    resolution_available = stream.streams.filter(adaptive=True, only_video=True, file_extension=file_extension)
    for resolution in resolution_available:
      if resolution.resolution in seen_quality or resolution.resolution is None:
        continue
      seen_quality[resolution.resolution] = resolution
      print("-", resolution.resolution)

  elif file_extension == "mp3":
    audio_available = stream.streams.filter(only_audio=True)
    for abr in audio_available:
      if abr.abr in seen_quality:
        continue
      seen_quality[abr.abr] = abr
      print("-", abr.abr)

  else:
    print("Error unavailable to recognize extension")
    sys.exit(1)

  while True:
    quality_choosed = input("What quality you prefer: ")
    if quality_choosed in seen_quality:
      break
    print("Invalid quality! Please choose again.")
    
  return seen_quality[quality_choosed]


def progress_func(stream, chunk, bytes_remaining):
  # Display download progress
  total_size = stream.filesize
  bytes_downloaded = total_size - bytes_remaining
  percent = (bytes_downloaded / total_size) * 100
  print(f"Download Progress: {percent:.2f}%")


def complete_func(stream, file_path):
  # Notify when download is complete
  print(f"Download completed: {file_path}")


main()