import pysrt
from pysrt.srttime import SubRipTime
import requests
import discord
from discord import Webhook, RequestsWebhookAdapter, File
import os
import re
import sys
import time
import datetime
import random

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
webhookid = WEBHOOK_ID
token = "YOUR_DISCORD_TOKEN"
webhook = Webhook.partial(webhookid, token, adapter=RequestsWebhookAdapter())

# Post Config
season_num = 1
episode_num = 2
start_post = True # Make a starting post showing how many episodes are left and how much time to go
toBeContinued = True # Add last frame to to be continued album
panoramas = True # Add upload panoramas to Panoramas album
post_text = f"Pokemon Season {season_num} Episode {episode_num} - Pokémon Emergency"
# Timing Config
delay = 30 # Seconds inbetween each post
wait_time = 3600 # Seconds after a group of posts
group = 25 # How many posts per group

# Path Config
frame_dir = r"C:/Users/framebot/bots/pokemonFrames/"
subtitles_dir = "C:/Users/framebot/bots/sources/srt"

# The folder where your images are stored (This only need to be changed if folder stucture changes. Currently set up for folders named like this: folder/s1e1sub/images)
frames = f"{frame_dir}s{season_num}e{episode_num}"
sub_frames = f"{frame_dir}s{season_num}e{episode_num}sub"
print(f"Image folder: {sub_frames} loaded")

# Create logs subfolder if it doesn't exist
logs_folder = 'logs'
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)
    print("Created logs folder!")

#testing timings
if connect_to_facebook.lower() == 'n':
    delay = 0 # Seconds inbetween each post
    wait_time = 1 # Seconds after a group of posts
    group = 50 # How many posts per group

# Load captions if there is one
pattern = f"{season_num}x{episode_num}" #naming pattern to look for
extension = ".srt"
match = False
captioned = False
for filename in os.listdir(subtitles_dir):
    full_path = os.path.join(subtitles_dir, filename)
    if os.path.isfile(full_path) and full_path.endswith(extension) and pattern in full_path:
        match = True
        break
if match:
    print(f"Subtitle file found {full_path}")
    captioned = True
else:
    print("No episode number match found. Filenames should have an x separating the season number from the episode number.")
if captioned:
    subs = pysrt.open(full_path)
    print(f"Subtitle file loaded")
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

else:
    index = 0
    print("No index file found. Starting from the beginning")
    
# Load the Blast Off counter from a file
blast_off_file = "counter_blastoff.txt"
if os.path.exists(blast_off_file):
    with open(blast_off_file) as b:
        blast_off_count = int(b.read())
    print(f"Current Team Rocket blast off count is {blast_off_count}")
else:
    blast_off_count = 0
    print("No Team Rocket blast off counter file found. Initializing")

# Determine how many frames there are
ListLength = len(os.listdir(sub_frames))
print(ListLength, "files found")

# Report how long this episode will run for
time_length_seconds = (ListLength - index) * (wait_time + (group * (delay + 5))) / group
time_length = datetime.timedelta(seconds = time_length_seconds)
time_length_hours = round(time_length_seconds / 3600, 1)
endtime = datetime.datetime.now() + time_length
endtime_minute_only = endtime.strftime("%Y-%m-%d %H:%M")
# Calculate the time to the end of the series
episodes_left = 1234 - (episode_num + 0) # Add previous season episodes to count
series_time_left = round(time_length_hours * episodes_left / 24 / 365, 1)
print(f"Running for {time_length_hours} hours")
print(f"EndTime: {endtime}")
if connect_to_discord.lower() == 'y':
    if index == 0:
        webhook.send(f"Facebook PokeBot started {post_text} Running until {endtime_minute_only}")
    else:
        webhook.send(f"Facebook PokeBot resuming at frame {index+1} Running until {endtime_minute_only}")
    
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
    
def make_album_post():
    # URL format and fields are according to facebook's API documentation
    # Since no API version is explicitly given in the link, requests will always use the latest API version
    url = (
        f"https://graph.facebook.com/{album_id}/photos?"
        f"caption={post_text}{album_status}&access_token={access_token}"
    )
    files = {
        'image': open(file_path, "rb")
    }
    # Send http POST request to /album-id/photos to add the frame in the album
    response = requests.post(url, files=files)
    return response.json()

def make_comment():
    # make request to add comment to post
    print(f"Adding comment to post {post_id}")
    comment_url = f"https://graph.facebook.com/{post_id}/comments?access_token={access_token}&message={comment_message}"
    response = requests.post(comment_url)
    return response.json()
    if response.status_code == 200:
        print("Comment added successfully!")
    else:
        print(f"Failed to add comment. Error: {response.json}")

comment_spacing = 0

if index == 0:    
    if connect_to_facebook.lower() == 'y':
        if start_post:
            post_message = f"Pokébot starting new episode {post_text} \nEstimated running time {time_length_hours} hours. End time: {endtime_minute_only} EDT\n\nThere are {episodes_left} regular episodes left. At the current pace it will take at least {series_time_left} years to finish."
            
            post_url = f"https://graph.facebook.com/me/feed?message={post_message}&access_token={access_token}"
            response = requests.post(post_url)

            # check the response status code
            if response.status_code == 200:
                print("Post created successfully!")
            else:
                print(f"Failed to create post. Status code: {response.status_code}")

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
        if captioned:
            caption = subs.at(timestamp)
        else:
            caption = ""
            
        caption_status = "Caption: "    
        if captioned:
            Status = f"{post_text}\nFrame {index+1}/{ListLength}\n{caption_status if caption else ''}{caption.text if caption else ''}"
        else:
            Status = f"{post_text}\nFrame {index+1}/{ListLength}"
        print(Status)
        
        blast_off_phrase = "off again"
        
        retries = 0
        success = False
        while not success and retries < 5:
            try:
                # post the image to Facebook
                if connect_to_facebook.lower() == 'y':
                    print(f"Time before post: {datetime.datetime.now()}")
                    post_response = make_post()
                    # Check if the request was successful to log info
                    if post_response.get('id'):
                        post_id = post_response['id']
                        
                        log_filename = f"s{season_num}e{episode_num}_log.txt"
                        log_file_path = os.path.join(logs_folder, log_filename)

                        with open(log_file_path, 'a') as logfile:
                            logfile.write(f"Frame {index+1}/{ListLength}\n")
                            logfile.write(f"Post ID: {post_id}\n")
                            if captioned:
                                if caption:
                                    logfile.write(f"Caption: {caption.text}\n")
                            logfile.write(f"Filename: {filename}\n")
                            logfile.write(f"Upload Time: {datetime.datetime.now()}\n")
                            logfile.write('\n')
                            
                    print(f"---> Post done! Time: {datetime.datetime.now()}")
                    post_id = post_response["post_id"]
                    # add a comment if phrase in caption only if 30 posts have passed
                    if captioned:
                        if blast_off_phrase in caption.text.lower() and comment_spacing > 30:
                            print("Waiting to make comment!")
                            time.sleep(30)
                            comment_message = f"Team Rocket has blasted off again {blast_off_count} times! -Pokébot"
                            comment_response = make_comment()
                            comment_spacing = 0
                            blast_off_count += 1
                            # Save progress to text file
                            with open("counter_blastoff.txt", "w") as b:
                                b.write(str(blast_off_count))
                        
                else:
                    print(f"Processing file {file}")
                    print(f"Comment spacing is {comment_spacing}")
                    
                    if captioned:
                        if blast_off_phrase in caption.text.lower() and comment_spacing > 30:
                            comment_message = f"Team Rocket has blasted off again {blast_off_count} times!"
                            print(f"Blast off found! {comment_message}")
                            time.sleep(300)
                            comment_spacing = 0
                            blast_off_count += 1
                success = True
            except:
                print(f'Error while posting image {file}')
                for e in sys.exc_info():
                    print(e)
                retries += 1
                print('Trying again in 5 minutes.')
                time.sleep(60*5)
        if not success:
            print(f'Failed to post image {file} after {retries} attempts')
            for e in sys.exc_info():
                                print(e)
            if connect_to_discord.lower() == 'y':
                webhook.send(f"facebook Bot failed to post image {file} after {retries} attempts.")
            # Wait for user input before exiting
            input("Too many errors. Press Enter to restart...")
        
        # Increment the index
        index += 1
        comment_spacing += 1
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
            

if connect_to_discord.lower() == 'y':
    webhook.send(f"Facebook Bot finished episode. Waiting to upload panoramas.")

os.remove("progress.txt")

# Add last image without caption to the To Be Continued album
if toBeContinued:
    album_id = 1234567890 #Replace this with your Facebook album id
    album_status = "\nTo Be Continued..."
    file_path = os.path.join(frames, file)
    post_response = make_album_post()
    print("To be continued added to album. Waiting to upload panoramas")
    time.sleep(wait_time/2)

if panoramas:
    panorama_folder = frames+"pano"
    album_id = 1234567890 #Replace this with your Facebook album id
    album_status = "\nPanorama"
    for filename in os.listdir(panorama_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"): # Only process image files
            file_path = os.path.join(panorama_folder, filename)
            post_response = make_album_post()
            time.sleep(5)
    print("All panoramas uploaded")

# Stats
with open('total_frames.txt', 'r') as total_frames_file:
    total_frames = int(total_frames_file.read())
    current_total = total_frames + ListLength
# Save new total to text file
with open("total_frames.txt", "w") as total_frames_file:
    total_frames_file.write(str(current_total))
    
# Self Promotion ending - Edit the post_message to whatever you want
with open('../promos.txt', 'r') as urls:
    lines = urls.readlines()

random_url = random.choice(lines)

if connect_to_facebook.lower() == 'y':
    post_message = f"To be continued...\n \nThis is a bot by Biochao, if you want to give a little tip you can do so here: https://ko-fi.com/biochao \n\nStats:\nPosted {current_total} frames since starting the page."
    post_url = f"https://graph.facebook.com/me/feed?message={post_message}&access_token={access_token}"
    response = requests.post(post_url)

    # check the response status code
    if response.status_code == 200:
        print("Post created successfully!")
    else:
        print(f"Failed to create post. Status code: {response.status_code}")

if connect_to_discord.lower() == 'y':
    time.sleep(wait_time/2) # Waiting some more before announcing time to start a new episode
    webhook.send(f"Facebook Bot ready to start new episode.")

# Wait for user input before exiting
input("End of the episode. Press Enter to restart...")
