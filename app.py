import os
import base64
import cv2
import requests
import json

# 確保 static 資料夾存在
if not os.path.exists('static'):
    os.makedirs('static')

# 拍攝影像
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法開啟攝影機")
        return None

    print("按下空白鍵以拍照...")
    image_path = os.path.join('static', 'image1.jpg')
    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法獲取影像")
            break

        cv2.imshow("capture", frame)
        key = cv2.waitKey(1)
        if key == 32:  # 空白鍵
            print("快門按下，保存影像...")
            cv2.imwrite(image_path, frame)
            print(f"影像已保存至: {image_path}")
            break

    cap.release()
    cv2.destroyAllWindows()
    return image_path

# 解析回應數據
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

# 生成詩句
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

    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print("未找到環境變數 GOOGLE_API_KEY，請設定 API 密鑰後再試")
        exit()

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
        json=dictionary
    )

    response_json = response.json()
    poem_text = get_value(response_json, "text")
    if not poem_text:
        print("無法提取生成的文本，請檢查 API 回應")
        print(response_json)
        poem_text = "無法生成詩句。"

    return poem_text

# 主程式
if __name__ == "__main__":
    image_path = capture_image()
    if image_path:
        poem = generate_poem(image_path)
        # 保存詩句到文件
        with open("static/poem.txt", "w", encoding="utf-8") as f:
            f.write(poem)
        print(f"詩句已保存：\n{poem}")
