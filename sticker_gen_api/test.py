import base64
import csv
import os
import json
import asyncio
import aiohttp
from slugify import slugify
from dotenv import load_dotenv
import openai


load_dotenv()
openai.api_key = "<OPENAI_API_KEY>"

async def generate_and_save_image(prompt, event_name):
    image_response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1
    )
    image_url = image_response.data[0].url

    folder_name = os.path.join("images", event_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = os.path.join(folder_name, f"{prompt.replace(' ', '_')}.png")
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as f:
                    f.write(await response.read())
            else:
                print(f"Failed to fetch image from {image_url}, status code {response.status}")

async def main(prompts, event_name):
    tasks = [generate_and_save_image(prompt, event_name) for prompt in prompts]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    prompts = ["winter landscape with snowman"]
    asyncio.run(main(prompts, 'test'))

