import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
from PIL import Image
import os
import re
import json


discord_token = "<YOUR_DISCORD_TOKEN>"

load_dotenv()
client = commands.Bot(command_prefix="*", intents=discord.Intents.all())

directory = os.getcwd()
print(directory)

def split_image(image_file):
    with Image.open(image_file) as im:
        # Get the width and height of the original image
        width, height = im.size
        # Calculate the middle points along the horizontal and vertical axes
        mid_x = width // 2
        mid_y = height // 2
        # Split the image into four equal parts
        top_left = im.crop((0, 0, mid_x, mid_y))
        top_right = im.crop((mid_x, 0, width, mid_y))
        bottom_left = im.crop((0, mid_y, mid_x, height))
        bottom_right = im.crop((mid_x, mid_y, width, height))

        return top_left, top_right, bottom_left, bottom_right

async def download_image(url, filename):
    response = requests.get(url)
    print(response.status_code)
    
    if response.status_code == 200:

        # Define the input and output folder paths
        input_folder = "input"
        output_folder = f"output/{filename}"

        # Check if the output folder exists, and create it if necessary
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Check if the input folder exists, and create it if necessary
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)

        with open(f"{directory}/{input_folder}/{filename}", "wb") as f:
            f.write(response.content)
        print(f"Image downloaded: {filename}")

        input_file = os.path.join(input_folder, filename)

        # Split the image
        top_left, top_right, bottom_left, bottom_right = split_image(input_file)
        # Save the output images with dynamic names in the output folder
        top_left.save(os.path.join(output_folder, "top_left.jpg"))
        top_right.save(os.path.join(output_folder, "top_right.jpg"))
        bottom_left.save(os.path.join(output_folder, "bottom_left.jpg"))
        bottom_right.save(os.path.join(output_folder, "bottom_right.jpg"))

        # Delete the input file
        os.remove(f"{directory}/{input_folder}/{filename}")
        
        # ## 완료 후 데이터 보내기 
        # url = "http://0.0.0.0:4000/download_image/"
        # data = {"text" : output_folder}
        # data = json.dumps(data)
        # res = requests.post(url, json = data)
        # if res.ok:
        #     print("complete_images")

@client.event
async def on_ready():
    print("Bot connected")

@client.event
async def on_message(message):
    
    print("***")
    print(message.content)
    print()
    
    file_name = message.content[:44]
    file_name = re.sub("\*", "", file_name).strip()
    file_name = file_name.strip().replace(" ", "_")
    
    print(message)
    print(message.attachments)
    print()
    
    for attachment in message.attachments:
        print(">>>")
        print(attachment.filename.lower())
        if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            print("if문")
            await download_image(attachment.url, file_name)
    
if __name__ == '__main__' :
    client.run(discord_token)