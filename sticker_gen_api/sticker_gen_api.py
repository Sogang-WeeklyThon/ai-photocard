from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio
from multiprocessing import Pool
import torch
from diffusers import DiffusionPipeline
import uvicorn
import openai
from rembg import remove


app = FastAPI()
# torch.multiprocessing.set_start_method('spawn')
# torch.multiprocessing.get_start_method()

class StickerRequest(BaseModel):
    prompts: List[str]

device = "cuda" if torch.cuda.is_available() else "cpu"
pipeline = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16).to(device)
pipeline.load_lora_weights("artificialguybr/StickersRedmond")

openai.api_key = "<OPENAI_API_KEY>"
model = "gpt-4o"
print("Model loaded successfully")


def translate_prompt(prompt_list):
    messages = [
    {"role": "system", "content": "You are a translator. Translate this list from Korean to English. Just Answer translated string output only."},
    {"role": "user", "content": ", ".join(prompt_list)}
    ]
    response = openai.ChatCompletion.create(model=model, messages=messages)
    response = response["choices"][0]["message"]["content"].replace('\n', '').strip()
    print(f"Translated from {', '.join(prompt_list)} to {response}")
    return response
    

def generate_sticker(prompt_list):
    prompt = ", ".join(prompt_list)
    prompt_full = f"{prompt} sticker without background"
    with torch.inference_mode():
        generated_image = pipeline(prompt_full).images[0]
    file_path = f"/home/mjk0307/otaku/otaku/sticker_gen_api/output/generated_{prompt_full.replace(', ', ' ').replace(' ', '_')}.png"
    
    output = remove(generated_image)
    output.save(file_path)  
    # generated_image.save(file_path)
    return file_path


def generate_images_with_multiprocessing(prompts):
    with Pool(processes=1) as pool:
        results = pool.map(generate_sticker, prompts)
    return results


@app.post('/generate-stickers')
async def generate_images(request: StickerRequest):
    print(request.prompts)
    if len(request.prompts) != 3:
        raise HTTPException(status_code=400, detail="Exactly three prompts are required.")

    # results = await asyncio.get_event_loop().run_in_executor(None, generate_images_with_multiprocessing, request.prompts)
    translated_prompts = translate_prompt(request.prompts)
    results = generate_sticker([translated_prompts])
    return {"message": "Stickers generated successfully", "file_paths": results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)