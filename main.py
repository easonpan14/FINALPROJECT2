from gtts import gTTS   #用於文字轉語音
from io import BytesIO  #允許在記憶體中操作二進制數據流
import os   #提供操作系統功能
import json
import base64

from flask import Flask, render_template, url_for 
import json
app = Flask(__name__)

import pygame   #用於播放音效
pygame.init()   #初始化模組

import cv2  #用於攝影機操作與影像處理

# take photo
cap = cv2.VideoCapture(0)  # 啟動攝影機
if not cap.isOpened():
    print("無法開啟攝影機")
    exit()

print("按下空白鍵以拍照...")

while True:
    ret, frame = cap.read()  # 捕獲影像
    if not ret:
        print("無法獲取影像")
        break

    cv2.imshow("capture", frame)  # 顯示捕獲的影像

    key = cv2.waitKey(1)  # 等待 1 毫秒以捕獲鍵盤事件
    if key == 32:  # 如果按下空白鍵 (ASCII 32)
        print("快門按下，保存影像...")
        cv2.imwrite(os.path.join('static', 'image1.jpg'), frame)
        break  # 退出循環

cap.release()  # 釋放攝影機資源
cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗

#os.system("fswebcam -r 800x600 --no-banner image1.jpg")

import time
time.sleep(1)   # 等待 1 秒，確保影像檔案準備就緒

# base64 encode
with open(os.path.join('static', 'image1.jpg'), "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())

# json
dictionary = {
    'contents':[
        {
            'parts':[
                {   'text': '把自己當作一個詩人，把看到的東西寫成詩，只要跟我說詩詞就好，不要輸出英文'},
                {    
                    'inline_data':{
                        'mime_type': 'image/jpeg',
                        'data': encoded_string.decode('utf-8')
                    }
                }
            ]
        }
    ]
}
 
#print(dictionary)

# Serializing json
json_object = json.dumps(dictionary)
 
# Writing to sample.json
with open("request.json", "w") as outfile:
    outfile.write(json_object)


# get API_KEY
with open("apikey.txt", "r") as f:
    first_line = f.readline()
API_KEY = first_line

# REST API
import requests
response = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key="+API_KEY+"", json=dictionary)

response_json = response.json()
#print(response_json)
def get_value(data, key):
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                return v
            else:
                value = get_value(v, key)
                if value is not None:
                    return value
    elif isinstance(data, list):
        for v in data:
            value = get_value(v, key)
            if value is not None:
                return value
    return None
#print(get_value(response_json, "text"))
#response_text = response_json['candidates'][0]['content']['parts'][0]['text']
response_text = get_value(response_json, "text")

#result = os.popen("curl https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key="+API_KEY+" -H 'Content-Type: application/json' -d @request.json ").read()
#print(result)
#response_text = json.loads(result)
print(response_text)

@app.route('/')
def hello_world():
    image_url = url_for('static', filename='image1.jpg')  # Get the image URL
    return render_template('index.html', poem=response_text, image_url=image_url)
if __name__ == '__main__':
    app.run(debug=True, port=5001)

# # TTS
# mp3_fp = BytesIO()
# tts = gTTS(text=response_text, lang='zh-TW')
# tts.write_to_fp(mp3_fp)

# # audio play
# mp3_fp.seek(0)
# pygame.mixer.init()
# pygame.mixer.music.load(mp3_fp)
# pygame.mixer.music.play()
# while pygame.mixer.music.get_busy():
#     pygame.time.Clock().tick(10)
