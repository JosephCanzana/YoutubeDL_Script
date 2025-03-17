from pytubefix import YouTube
import os
import shutil
import sys
import subprocess

def main():

  url = input("YouTube URL: ")

  # Go in download folder if doesn't exist create new
  Downloads_path = "Your/path/to/downloads"
  os.makedirs(Downloads_path, exist_ok=True)
  try:
    yt_url = YouTube(url, on_progress_callback=progress_func, on_complete_callback=complete_func)
  except:
    print("Error")
    sys.exit(1)  # Exit if there's an error initializing YouTube object
  
  extension = input("What media type [mp4/mp3]? ")
  quality = available_streams(yt_url, extension)
  print_info(yt_url, quality, extension)

  # Ask if continue to download
  answer = input("Continue to download? [y/n]: ").lower().strip()
  if answer == 'n':
    print(
          "====Download terminated==== \n "
          "====Program Done===="
          )
    sys.exit(1)

  initial_path = download(quality,yt_url)
  final_path = path_exist(initial_path, Downloads_path, yt_url, extension)

  final_path = shutil.move(final_path, Downloads_path)
  print("Final Path:", final_path)
  print("Program Done")


def print_info(video, q, e):
  print(
      f"Title: {video.title}\n"
      f"Author: {video.author}"
        )
  
  if e == "mp4":
    print("Resolution:", q.resolution)
  else:
    print("Abr:", q.abr)


def download(stream, url):
  # Download and store the path of download for transferring in downloads folder
  path = stream.download()
  if stream.type == "video":

    path_parts = path.split("/")
    initial_path = "/".join(path_parts[:len(path_parts) - 1])
    video_path = f"{initial_path}/video.mp4"
    os.rename(path, video_path)
    print(video_path)

    # Audio quality of the video
    print("Choose audio quality: ")
    audio = available_streams(url, "mp3")
    audio_path = audio.download()
    output_path = f"{initial_path}/{stream.title}.mp4"
    
    # Merge using ffmpeg
    command = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{output_path}"'
    subprocess.run(command, shell=True)

    # Cleanup
    os.remove(video_path)
    os.remove(audio_path)
    path = output_path

  return path


def path_exist(initial_path, download_path, video, extension):
  # If extension duplicate already exist continue adding 1 at the end of file name
  print("-" * len(initial_path))
  path_exist = os.path.exists(f"{download_path}/{video.title}.{extension}")
  if path_exist:
    counter = 1

    while path_exist:
      # The initial path where the file is downloaded
      file_parts = initial_path.split(".")
      file_name = ".".join(file_parts[:len(file_parts) - 1])
      file_extension = file_parts[len(file_parts) - 1]

      new_video_path = f"{file_name}({counter}).{file_extension}"

      # Check if it exists already in download folder creating a duplicate
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
  total_size = stream.filesize
  bytes_downloaded = total_size - bytes_remaining
  percent = (bytes_downloaded / total_size) * 100
  print(f"Download Progress: {percent:.2f}%")


def complete_func(stream, file_path):
  print(f"Download completed: {file_path}")


main()