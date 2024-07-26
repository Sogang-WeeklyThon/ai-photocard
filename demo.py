import gradio as gr
import requests
from PIL import Image
import os
import shutil
from rembg import remove
import time


ratio = None
midjourney_prompt = None
person_path = None 
frame_path = None 
sticker_path = None
send_image_path = None 
final_message = ""


def process_file(file_path):
    global ratio, person_path
    output_dir = "/home/mjk0307/otaku/otaku/background_removed"
    os.makedirs(output_dir, exist_ok=True) 
    
    filename = os.path.basename(file_path)
    output_file_path = os.path.join(output_dir, filename)
    
    shutil.copyfile(file_path, output_file_path)
    
    with Image.open(output_file_path) as image:
        w, h = image.width, image.height
        ratio = f"{w}:{h}"
        output = remove(image)
        processed_output_path = os.path.join(output_dir, f"processed_{filename}")
        output.save(processed_output_path.replace('.jpg', '.png').replace(".jpeg",".png")) 
        person_path = processed_output_path.replace('.jpg', '.png').replace(".jpeg",".png")
    
    return output


def generate_midjourney(prompts):
    global ratio, frame_path
    url = 'http://localhost:4000/prompt_optimizer'
    data = {"user_prompt": prompts, "image_ratio": ratio}
    prompt_response = requests.post(url, json=data)
    if prompt_response.status_code == 200:
        prompt_result = prompt_response.json()
 
    send_url = 'http://localhost:4000/send_prompt'
    data = {"converted_prompt": prompt_result}
    response = requests.post(send_url, json=data)
    
    n = 0
    while not os.path.exists(f'midjourney_api/output/{prompt_result[:42].strip().replace(" ", "_")}'):
        if n >= 40 :
            print("time out error")
            return 
        print("키라키라 최애 배경 생성 중...")
        time.sleep(1)
        n += 1
        
        
    time.sleep(2)
    frame_path = f'midjourney_api/output/{prompt_result[:42].strip().replace(" ", "_")}' 
    image1 = Image.open(os.path.join(frame_path, 'top_left.jpg'))
    image2 = Image.open(os.path.join(frame_path, 'top_right.jpg'))
    image3 = Image.open(os.path.join(frame_path, 'bottom_left.jpg'))
    image4 = Image.open(os.path.join(frame_path, 'bottom_right.jpg'))
    
    frame_path = {
        "첫 번째": os.path.join(frame_path, 'top_left.jpg'),
        "두 번째": os.path.join(frame_path, 'top_right.jpg'),
        "세 번째": os.path.join(frame_path, 'bottom_left.jpg'),
        "네 번째":os.path.join(frame_path, 'bottom_right.jpg')
    }
    
    return image1, image2, image3, image4
    

def generate_stickers(prompts):
    global sticker_path
    url = 'http://localhost:8888/generate-stickers'  
    data = {'prompts': prompts.split(", ")}  
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        sticker_path = result['file_paths']  
        image = Image.open(sticker_path)  
        return image
    else:
        return "Error: " + response.json()['detail']  



def integrate_photo(selected_frame):
    global person_path, frame_path, sticker_path, send_image_path
    selected_frame_path = frame_path[selected_frame]
    
    url = 'http://localhost:8123/pb_integration'  
    data = {'person': person_path, 'background': selected_frame_path}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        pb_path = response.json()


    url = 'http://localhost:8123/pbs_integration' 
    data = {'pb_path': pb_path, 'sticker_path': sticker_path} 
    response = requests.post(url, json=data)
    print(response)
    if response.status_code == 200: 
        send_image_path = response.json()

    return Image.open(send_image_path)


def send_message(phone_number):
    global final_message, send_image_path
    url = "http://localhost:8815/send"
    data = {"phone_number": str(phone_number), "send_image_path": send_image_path}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        final_message = "메시지가 전송되었습니다."
        
    return result


custom_css = """
#banner-image {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 40%;
}
"""

title = """<h1 align="center"> 💓 최애를 특별하게, 나만의 아이돌 포토카드 꾸미기 AI 💕 </h1>"""

with gr.Blocks(theme='ParityError/Anime', analytics_enabled=False, css=custom_css) as demo:
    gr.HTML(title)
    with gr.Column():
        gr.Markdown("꾸미고 싶은 최애의 사진을 업로드해주세요!")
        with gr.Row():
            image_input = gr.Interface(
                            fn=process_file,
                            inputs=["file"],
                            outputs=gr.Image(height=300)
                        )
            
     
        with gr.Column():
            gr.Markdown("스티커 생성을 위해 프롬프트를 3개 입력해주세요!")
        with gr.Row():
            sticker_prompt_input = gr.Textbox(label="스티커 생성 프롬프트 3개 예시: 노랑, 하트, 반짝반짝")
            sticker_gen = gr.Interface(
                fn=generate_stickers,
                inputs=sticker_prompt_input,
                outputs=gr.Image(height=150)
            )
        
        with gr.Column():
            gr.Markdown("테두리 생성을 위한 프롬프트를 입력해 주세요!")
            prompt_input = gr.Textbox(label="테두리 생성 프롬프트 예시: 핑크색의 사랑스러운 분위기로 꾸며줘.")
            
            with gr.Row():
                image_output_1 = gr.Image(height=150)
                image_output_2 = gr.Image(height=150)
                image_output_3 = gr.Image(height=150)
                image_output_4 = gr.Image(height=150)
            
            frame_output = gr.Button("Generate")
            frame_output.click(fn=generate_midjourney, inputs=prompt_input, outputs=[image_output_1, image_output_2, image_output_3, image_output_4])
            
                          
        # with gr.Column():
        #     gr.Markdown("아래 체크박스에서 테두리 이미지를 한 개 선택해주세요! ")
            
        
        with gr.Column():
            gr.Markdown("최종 결과입니다!!")
            
        with gr.Row():
            final_result = gr.Interface(
                        fn=integrate_photo,
                        inputs=gr.Radio(
                            label="selected_frame",
                            choices=["첫 번째", "두 번째", "세 번째", "네 번쨰"],
                            value = "첫 번째",
                            info="테두리 이미지를 선택해주세요! 아래 체크박스에서 테두리 이미지를 한 개 선택해주세요!",
                            interactive=True,
                        )
            ,
                        outputs=gr.Image(height=500)
                    )
        
        with gr.Column():
            gr.Markdown("사진 전송을 위해 핸드폰 번호를 입력해주세요!!")
        with gr.Row():
            phone_number = gr.Textbox(label="예시: 010-1234-5678")
            message_box = gr.Interface(
                        fn=send_message,
                        inputs=phone_number,
                        outputs = None
                    )
            if final_message:
                gr.Markdown(final_message)

demo.launch(share=True, debug=True)
