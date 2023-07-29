# Pokemon FrameBot
Every Pokemon Frame in Order Facebook Bot
https://www.facebook.com/pokeFrames

Parts modified from spacebruce's Monogatari bot and YAFOT-Facebook bot

Disclamer: I'm not a python developer I don't know what I'm doing... Most of this was created with the help of ChatGPT... If you think you can make this bot better feel free to make a pull request.

Features include:
  
  • Option to read a subtitle file and add the correct caption to the post
  
  To use srt files for captions frames need to be named in milliseconds by ffmpeg

  Automatic srt detection needs srt files to have season and episode numbers in the file name like so "1x24" where 1 is the season number and 24 is the episode number.

  • Logging post id's to a text file with other info like post time, index, current caption
  
  • Option for Discord error reporting and end of episode messages
  
  • Option to not connect to Facebook for testing
  
  • groups of posts with variable delay
  
  • progress file to resume incase of errors or interuptions

  • If using a subtitle file it can detect a word or phrase on a post and make a comment. I'm keeping track of how many times Team Rocket says "We're blasting off again!"


How to use:
Insert your Facebook page id and token
https://github.com/boidushya/FrameBot/blob/master/generateToken.md

Insert your Discord webhook if you want status reports


Set the frame_dir, this is the folder that contains the episode folders. 
The bot will use the season number and episode number you set provided your episode folders are named like this: "s1e1sub" This can be changed by editing the sub_frames variable.


If you want to have subtitles in the post set the folder where your srt files are with subtitles_dir and the bot will find the correct file for the episode using regex with the season_num and episode_num variables.

Execute the Python file

Answer the startup options questions

Done!
