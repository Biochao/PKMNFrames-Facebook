import pysrt
from pysrt.srttime import SubRipTime
import requests
import discord
from discord import Webhook, RequestsWebhookAdapter, File
import os
import sys
import time
import datetime

# Facebook page config
connect_to_facebook = input('Do you want to connect to facebook (y/n)? ')
# Replace ACCESS_TOKEN with your Page Access Token
access_token="ACCESS_TOKEN"

page_id = PAGE_ID # Replace PAGE_ID with the ID of your Facebook page

# Test credentials
if connect_to_facebook.lower() == 'y':
    try:
        url = f"https://graph.facebook.com/{page_id}"
        params = {
            "access_token": access_token,
            "fields": "name"
        }
        response = requests.get(url, params=params)
        page_name = response.json()["name"]
        print(f"Connected to Facebook page {page_name}")
    except:
        print("facebook not OK, try again in 60 seconds")
        for e in sys.exc_info():
            print(e)
        time.sleep(60)

# Error Notifications?
connect_to_discord = input('Do you want to report to Discord (y/n)? ')
# Discord Error Reporting
webhookid = WEBOOK_ID
token = "YOUR_DISCORD_TOKEN"
webhook = Webhook.partial(webhookid, token, adapter=RequestsWebhookAdapter())

# Post Config
season_num = 1
episode_num = 2
post_text = f"Pokemon Season {season_num} Episode {episode_num} - Pokemon Emergency!"
pokemon = ""
episode_name = "Pokemon-1x02-PokemonEmergency!" # Name of subtitle file
# Timing Config
delay = 30 # Seconds inbetween each post
wait_time = 3600 # Seconds after a group of posts
group = 18 # How many posts per group

# Path Config
frame_dir = r"C:/Users/framebot/bots/pokemonFrames/"

# The folder where your images are stored (This only need to be changed if folder stucture changes. Currently set up for folders named like this: folder/s1e1/images)
sub_frames = f"{frame_dir}s{season_num}e{episode_num}sub"
print(f"Image folder: {sub_frames} loaded")

# Subtitle Config
source_dir = "C:/Users/framebot/bots/sources/Season 01/"
sub_type = ".srt" # Format of subtitles
  
# Use a subtitle file?
subtitled = input('Does this episode have an external subtitle file (y/n)? ')
if subtitled.lower() == 'y':
    subs = pysrt.open(f"{source_dir}{episode_name}{sub_type}") # Full location of the subtitle file
    print(f"Subtitle file: {source_dir}{episode_name}{sub_type} loaded")
else:
    subs = ""

# Confirmation to start   
print(post_text)
input("Press enter to start")
  
# Initialize a counter variable to track how many frames of a group have been posted
counter = 0

# Load the index from a file (or initialize it to 0 if the file doesn't exist)
index_file = "progress.txt"
if os.path.exists(index_file):
    with open(index_file) as f:
        index = int(f.read())
    print("Progress file found. Resuming.")
    if connect_to_discord.lower() == 'y':
        webhook.send(f"facebook Bot resuming at frame {index+1}")
else:
    index = 0
    print("No index file found. Starting from the beginning")
    if connect_to_discord.lower() == 'y':
        webhook.send(f"New facebook Bot started {post_text}")

# Determine how many frames there are
ListLength = len(os.listdir(sub_frames))
print(ListLength, "files found")

# Report how long this episode will run for
time_length_seconds = (ListLength - index) * (wait_time + (group * (delay + 4))) / group
time_length = datetime.timedelta(seconds = time_length_seconds)
time_length_hours = time_length.total_seconds() / 3600
endtime = datetime.datetime.now() + time_length
print(f"Running for {time_length_hours} hours")
print(f"EndTime: {endtime}")
if connect_to_discord.lower() == 'y':
    webhook.send(f"Running until {endtime}")
    
def make_post():
    # URL format and fields are according to facebook's API documentation
    # Since no API version is explicitly given in the link, requests will always use the latest API version
    url = (
        f"https://graph.facebook.com/{page_id}/photos?"
        f"caption={Status}&access_token={access_token}"
    )
    files = {
        'image': open(file_path, "rb")
    }
    # Send http POST request to /page-id/photos to make the post
    response = requests.post(url, files=files)
    return response.json()

# post each image in the folder starting from the saved index
for i, file in enumerate(os.listdir(sub_frames)):
    # Check if the file is an image
    if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.gif'):
        # Skip files before the saved index
        if i < index:
            continue
        print(index)
        file_path = os.path.join(sub_frames, file)
        filename = file
        # Split the extension from the filename
        base_name, file_extension = os.path.splitext(file)
        
        # Create a SubRipTime instance with the time in milliseconds
        timestamp = int(base_name[:8])
        if subtitled.lower() == 'y':
            caption = subs.at(timestamp)
        else:
            caption = ""
        caption_status = "Caption: "    
        Status = f"{post_text}\nFrame {index+1}/{ListLength}\n{caption_status if caption else ''}{caption.text if caption else ''}"
        print(Status)
        
        retries = 0
        success = False
        while not success and retries < 5:
            try:
                # post the image to Facebook
                if connect_to_facebook.lower() == 'y':
                    print(f"Time before post: {datetime.datetime.now()}")
                    post_response = make_post()
                    print(f"---> Post done! Time: {datetime.datetime.now()}")
                    print(f"Post response: {post_response}")
                else:
                    print(f"Processing file {file}")
                success = True
            except:
                print(f'Error while posting image {file}')
                for e in sys.exc_info():
                    print(e)
                retries += 1
                print('Trying again in 3 minutes.')
                time.sleep(60*3)
        if not success:
            print(f'Failed to post image {file} after {retries} attempts')
            for e in sys.exc_info():
                                print(e)
            if connect_to_discord.lower() == 'y':
                webhook.send(f"facebook Bot failed to post image {file} after {retries} attempts. Cause: {e}")
            # Wait for user input before exiting
            input("Too many errors. Press Enter to restart...")
        
        # Increment the index
        index += 1
        # Save progress to text file
        with open("progress.txt", "w") as f:
            f.write(str(index))
        
        # Sleep for a specified delay before posting the next frame
        print(f"Waiting for {delay} seconds till the next frame\n")
        time.sleep(delay)
        
        # Increment the counter
        counter += 1

        # If the counter has reached 5, sleep for the specified wait time
        # before resetting the counter and continuing to post the next batch of frames
        if counter == group:
            print(f"Group posted waiting for {wait_time} seconds\n")
            time.sleep(wait_time)
            counter = 0
            
# Wait for user input before exiting
if connect_to_discord.lower() == 'y':
    webhook.send(f"facebook Bot finished episode")
os.remove("progress.txt")
input("End of the video. Press Enter to restart...")
