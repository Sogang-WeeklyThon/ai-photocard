import os

import uvicorn
from PIL import Image
from fastapi import FastAPI
from rembg import remove


app = FastAPI()

@app.get("/heath")
async def health_check():
    return "healthy!"


@app.post("/remove")
async def remove_background(request:dict):
    file_list = os.listdir("./background_removed")
    n = len(file_list)
    output_file_name = f'{n}.png'
    image = Image.open(request["path"])
    output = remove(image)
    output_path  = os.path.join("./background_removed", output_file_name)
    output.save(output_path)
    image.close()

    return output_path

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)


