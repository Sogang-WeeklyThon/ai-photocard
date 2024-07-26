from diffusers import DiffusionPipeline
import torch


device = "cuda" if torch.cuda.is_available() else "cpu"
pipeline = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0").to(device)
pipeline.load_lora_weights("artificialguybr/StickersRedmond")

print("Model loaded successfully")

prompt = "white, winter, cute sticker without background"


with torch.inference_mode():
    generated_image = pipeline(prompt).images[0]


generated_image.save("generated_image2.png")
