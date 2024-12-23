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

# 確保 static 資料夾存在
if not os.path.exists('static'):
    os.makedirs('static')

# 啟動攝影機並捕捉影像（執行一次）
def capture_image():
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
    return image_path

# 確認影像檔案
def ensure_image_exists(image_path):
    if not os.path.exists(image_path):
        print("影像檔案不存在，請檢查是否保存成功")
        exit()

# 發送影像到 OpenAI API 並獲取詩句
def generate_poem(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

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

    # 確認 API_KEY 是否存在於環境變數
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print("未找到環境變數 GOOGLE_API_KEY，請設定 API 密鑰後再試")
        exit()

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
        json=dictionary
    )

    response_json = response.json()

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

    return response_text

# 啟動 Flask 網頁伺服器
@app.route('/')
def hello_world():
    image_url = url_for('static', filename='image1.jpg')  # 獲取影像的 URL
    return render_template('index.html', poem=poem_text, image_url=image_url)

if __name__ == '__main__':
    # 執行拍照與生成詩句一次
    image_path = capture_image()
    ensure_image_exists(image_path)
    poem_text = generate_poem(image_path)

    # 啟動 Flask 網頁伺服器
    app.run(debug=True, port=5001)
