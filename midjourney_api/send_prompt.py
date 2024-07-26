import json
import requests

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

import openai
import time 
import re

class Item(BaseModel):
    text : str

app = FastAPI()

def generate_gpt(gpt_ver, query):
    """ Generate a GPT response. """
    retries = 3
    while retries > 0:
        try:
            messages = [{"role": "user", "content": query}]
            response = openai.ChatCompletion.create(model=gpt_ver, messages=messages)
            res = response["choices"][0]["message"]["content"]
            return res
        except Exception as e:
            if e:
                print(e)
                print("Timeout error, retrying...")
                retries -= 1
                time.sleep(3)
            else:
                raise e
    print("API is not responing, moving on...")
    return ""

@app.post("/user_prompt")
def get_prompt(user_prompt : str):
    return user_prompt

@app.post("/image_ratio")
def get_ratio(image_ratio : str):
    return image_ratio
    
@app.post("/prompt_optimizer")
async def prompt_optimizer(request : dict):
    user_prompt = request["user_prompt"]
    image_ratio = request["image_ratio"]
    
    ## openai 
    openai.api_key = "<OPENAI_API_KEY>"
    model = "gpt-4o"

    ## prompt template
    prompt_template = '''[Context]
- 너는 프롬프트 optimizer야. [User Prompt]에 입력된 색상, 아이템, 분위기를 캐치해서 이를 길고 상세하게 [Converted Prompt]로 변환할거야. [Converted Prompt]는 영어로 작성되어야 해. 

[Objective]
- [User Prompt]에 나타난 색상, 아이템, 분위기를 특히 신경써야 해.
- [Converted Prompt]의 기본적인 템플릿 안에서, [User Prompt]가 원하는 색상, 아이템, 분위기 등을 낼 수 있게 약간만 수정하는 것이 목표야. 

## 1
[User Prompt]
검정색 하트와 사슬로 구성된 탑꾸 완성해줘.

[Converted Prompt]
An black frame with heart-shaped chains, featuring the black and grat and white hears and space for text or pictures on a white background. The design should include a large empty area in front of the chain border allowing room for your own messages or images within it. Use dark colors like gray and blacks to make a mysterious and kitch composition in the style. Add details such as blur effects and 3d hearts around the edges. 

## 2
[User Prompt]
즈하랑 어울리는 발레코어 스타일 흰색과 연한 핑크 위주로

[Converted Prompt]
An white frame with a few embroidery stickers, featuring the ballet-core and ribbons and hearts and white hears and space for text or pictures on a white background. The design should include a large empty area in front of the sticker border allowing room for your own messages or images within it. Use bright and elegance colors like pink or white to make romantic and girlish composition in the style. Add details such as blur effects and embroidery stickers around the edges.

## 3
[User Prompt]
하얀색 배경이랑 하늘색 바다 속 인어공주처럼

[Converted Prompt]
An blue frame with stickers, featuring the stars and sea and fishes and grat and white hears and space for text or pictures on a white background. The design should include a large empty::5 area in front of the border allowing room for your own messages or images within it. Use blue and dark blue colors like ocean to make a mysterious and romantic ocean composition in the style.

## 5 
[User Prompt]
{first_prompt} 이런 분위기의 프레임을 만들어줘.

[Converted Prompt]
'''

    query=prompt_template.format(first_prompt=user_prompt)
    result = generate_gpt(model, query)
    while not result:
        result = generate_gpt(model, query)
    
    result = re.sub("\[Converted Prompt\]", "", result)
    result = result+f" The design should include a large empty::5 area in front of the border allowing room for your own messages or images within it. --ar {image_ratio} --iw 2"
    result = result.strip()
    
    return result

@app.post("/send_prompt")
async def send_prompt(request : dict):
    converted_prompt = request["converted_prompt"]
    
    with open("config.json", "r") as json_file:
        params = json.load(json_file)
        
    header = {
        'authorization': params['authorization']
    }

    payload = {
        'type': 2, 
        'application_id': params['application_id'],
        'guild_id': params['guild_id'],
        'channel_id': params['channelid'],
        'session_id': params['session_id'],
        'data': {
            'version': params['version'],
            'id': params['id'],
            'name': 'imagine',
            'type': 1,
            'options': [{'type': 3, 'name': 'prompt', 'value': converted_prompt}],
            'attachments': []
        }
    }

    r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)

    return 

# @app.post("/download_image")
# async def get_image_path(data: Item):
#     print(data.text)
#     return data.text

if __name__ == '__main__' :
    uvicorn.run(app, host="0.0.0.0", port=4000)
    
    ## user_prompt는 분위기와 색상 위주로만 적는 것이 좋음! 
    # print(prompt_optimizer("하양색과 분홍색을 바탕으로 사랑스러운 프레임을 만들어줘", "2:3"))