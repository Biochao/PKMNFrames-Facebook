import pysrt
from pysrt.srttime import SubRipTime
import facebook
import discord
from discord import Webhook, RequestsWebhookAdapter, File
import os
import logging
import time
import datetime

logging.basicConfig(filename='errors.log', level=logging.ERROR)

# Post Config
season_num = 1
episode_num = 1
post_text = f"Pokemon Season {season_num} Episode {episode_num} - Pokemon - I Choose You!"
pokemon = ""
episode_name = "Pokemon-1x01-Pokemon-IChooseYou!" # Name of subtitle file
# Timing Config
delay = 10 # Seconds inbetween each post
wait_time = 1800 # Seconds after a group of posts
group = 13 # How many posts per group

# Path Config
frame_dir = r"C:/Users/framebot/bots/pokemonFrames/"

# The folder where your images are stored (This only need to be changed if folder stucture changes. Currently set up for folders named like this: folder/s1e1/images)
sub_frames = f"{frame_dir}s{season_num}e{episode_num}sub"
print(f"Image folder: {sub_frames} loaded")

# Subtitle Config
source_dir = "C:/Users/framebot/bots/sources/Season 01/"
sub_type = ".srt" # Format of subtitles

# Facebook page config
connect_to_facebook = input('Do you want to connect to facebook (y/n)? ')
# Replace ACCESS_TOKEN with your Page Access Token
graph = facebook.GraphAPI(access_token="YOUR_ACCESS_TOKEN_HERE")

page_id = 116986881273972 # Replace PAGE_ID with the ID of your Facebook page

# Test credentials
if connect_to_facebook.lower() == 'y':
    page = graph.get_object(id=page_id, fields='name')
    try:
        print(f"Connected to Facebook page {page['name']}")
    except facebook.GraphAPIError as e:
        logging.exception(e)
        print("facebook not OK, try again in 30 seconds")
        time.sleep(30)
  
# Error Notifications?
connect_to_discord = input('Do you want to report to Discord (y/n)? ')
  
# Discord Error Reporting
webhookid = 123456789
token = "DISCORD_TOKEN"
webhook = Webhook.partial(webhookid, token, adapter=RequestsWebhookAdapter())

# Use a subtitle file?
subtitled = input('Does this episode have an external subtitle file (y/n)? ')
if subtitled.lower() == 'y':
    subs = pysrt.open(f"{source_dir}{episode_name}{sub_type}") # Full location of the subtitle file
else:
    subs = ""
  


# Initialize a counter variable to track how many frames of a group have been posted
counter = 0
Now = datetime.datetime.now()

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
# Calculate the time length in seconds
time_length_seconds = (ListLength - index) * wait_time / group

# Create a timedelta object to represent the time length
time_length = datetime.timedelta(seconds = time_length_seconds)

# Convert the time length to hours
time_length_hours = time_length.total_seconds() / 3600

# Calculate the end time by adding the time length to the current time
endtime = datetime.datetime.now() + time_length

print(f"Running for {time_length_hours} hours")
print(f"EndTime: {endtime}")
if connect_to_discord.lower() == 'y':
    webhook.send(f"Running until {endtime}")
    
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
        while not success and retries < 10:
            try:
                # post the image to Facebook
                if connect_to_facebook.lower() == 'y':
                        image = open(file_path, 'rb')
                        graph.put_photo(image=image, message=Status)
                else:
                    print(f"Processing file {file}")
                success = True
            except:
                print(f'Error while posting image {file}')
                retries += 1
                print('Trying again in 30 seconds.')
                if connect_to_discord.lower() == 'y':
                    webhook.send(f"facebook Bot encountered an error and is trying again")
                time.sleep(30)
        if not success:
            print(f'Failed to post image {file} after {retries} attempts')
            if connect_to_discord.lower() == 'y':
                webhook.send(f"facebook Bot failed to post image {file} after {retries} attempts")
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
