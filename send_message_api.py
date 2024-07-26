import os
import json

import cv2
from src.lib import message, storage
from fastapi import FastAPI
import uvicorn

def shrink_under_limit(path):
    size = os.path.getsize(path)
    if size > 1024 * 200:
        image = cv2.imread(path)
        image = cv2.resize(image, (int(image.shape[1]//1.05),int(image.shape[0]//1.05)))
        cv2.imwrite(path, image)
        return shrink_under_limit(path)
    return path

app = FastAPI()

@app.post("/send")
async def sendmessage(request:dict):
    try:
        print(request)
        phone_number = request["phone_number"]
        phone_number = str(phone_number).replace("-","")
        print(phone_number)
        send_image_path = request["send_image_path"]
        shrink_under_limit(send_image_path)
        
        res = storage.upload_image(send_image_path).json()
        fileId = res["fileId"]
        
        data = {
            'messages':[
                {
                    "to":[phone_number],
                    "from":"01021370817",
                    "subject":"포토카드",
                    "imageId":fileId,
                    "text":"생성된 포토카드입니다!"
                }
            ]
        }
        
        res = message.send_many(data)
        print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
        return json.dumps(json.loads(res.text), indent=2, ensure_ascii=False)
    except Exception as e:
        print(e)
        return "failed to send message."

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0",port=8815)