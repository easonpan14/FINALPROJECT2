from gtts import gTTS
from io import BytesIO
import os
import json
import base64
from flask import Flask, render_template, url_for
import pygame
import cv2
import requests
import time

app = Flask(__name__)
pygame.init()

# 檢查並創建 static 資料夾
if not os.path.exists('static'):
    os.makedirs('static')

# 啟動攝影機並捕捉影像
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("無法開啟攝影機")
    exit()

print("按下空白鍵以拍照...")
while True:
    ret, frame = cap.read()
    if not ret:
        print("無法獲取影像")
        break

    cv2.imshow("capture", frame)
    key = cv2.waitKey(1)
    if key == 32:  # 空白鍵
        print("快門按下，保存影像...")
        try:
            image_path = os.path.join('static', 'image1.jpg')
            cv2.imwrite(image_path, frame)
            print(f"影像已保存至: {image_path}")
        except Exception as e:
            print(f"保存影像失敗: {e}")
        break

cap.release()
cv2.destroyAllWindows()

# 等待影像文件準備完成
time.sleep(1)

# 檢查影像是否存在
image_path = os.path.join('static', 'image1.jpg')
if not os.path.exists(image_path):
    print("影像檔案不存在，請檢查是否保存成功")
    exit()

# 將影像轉為 Base64
with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())

# 構造 JSON 請求
dictionary = {
    'contents': [
        {
            'parts': [
                {'text': '把自己當作一個詩人，把看到的東西寫成詩，只要跟我說詩詞就好，不要輸出英文'},
                {
                    'inline_data': {
                        'mime_type': 'image/jpeg',
                        'data': encoded_string.decode('utf-8')
                    }
                }
            ]
        }
    ]
}

# 確認 API_KEY 文件是否存在
if not os.path.exists("apikey.txt"):
    print("找不到 apikey.txt 文件，請確保它存在並包含您的 API KEY")
    exit()

# 讀取 API_KEY
with open("apikey.txt", "r") as f:
    API_KEY = f.readline().strip()
    if not API_KEY:
        print("API_KEY 為空，請在 apikey.txt 中填入您的 API 密鑰")
        exit()

# 發送 REST API 請求
response = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
    json=dictionary
)

response_json = response.json()

# 提取生成的文本
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

response_text = get_value(response_json, "text")
if not response_text:
    print("無法提取生成的文本，請檢查 API 回應")
    print(response_json)
    exit()

print(response_text)

# 啟動 Flask 網頁伺服器
@app.route('/')
def hello_world():
    image_url = url_for('static', filename='image1.jpg')  # 獲取影像的 URL
    return render_template('index.html', poem=response_text, image_url=image_url)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
