from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

import uvicorn


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="/home/mjk0307/otaku/otaku/")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/editor.html")
# async def editor(request:Request):
#      return templates.TemplateResponse("/editor.html", {"request":request})

@app.get("/editor")
async def redirect_to_editor():
     return RedirectResponse(url="http://localhost:7861")

@app.get("/how_to_use.html")
async def editor(request:Request):
     return templates.TemplateResponse("/how_to_use.html", {"request":request})

@app.get("/products.html")
async def editor(request:Request):
     return templates.TemplateResponse("/products.html", {"request":request})


if  __name__ =="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)