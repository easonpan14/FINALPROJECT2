import os
import base64
import cv2
import requests
import json

def ensure_static_folder():
    """確保 static 資料夾存在"""
    if not os.path.exists('static'):
        os.makedirs('static')

def capture_image():
    """拍攝影像"""
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

def get_value(data, key):
    """遞迴搜索 JSON 中的指定鍵值"""
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

def format_text(text, line_length=30):
    """將文本格式化為指定的行長"""
    lines = []
    while len(text) > line_length:
        split_index = text.rfind(' ', 0, line_length)
        if split_index == -1:
            split_index = line_length
        lines.append(text[:split_index])
        text = text[split_index:].strip()
    if text:
        lines.append(text)
    return '\n'.join(lines)

def generate_content(image_path, prompt):
    """根據提示生成內容"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    dictionary = {
        'contents': [
            {
                'parts': [
                    {'text': prompt},
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
    content_text = get_value(response_json, "text")
    if not content_text:
        print("無法提取生成的文本，請檢查 API 回應")
        print(response_json)
        content_text = "無法生成內容。"

    return content_text

def main():
    ensure_static_folder()

    print("選擇功能：")
    print("1. 生成詩句 ")
    print("2. 生成文案 ")
    print("3. 輸出惡搞句子 ")
    print("4. 輸出笑話或諧音梗 ")
    print("5. 人格分析 ")
    print("6. 適配度分析 ")

    try:
        choice = int(input("請輸入選項 (1-6)："))
    except ValueError:
        print("無效輸入，請輸入數字 1 到 6。")
        return

    prompts = {
        1: "把自己當作一個詩人，把看到的東西寫成詩，只要跟我說詩詞就好，不要輸出英文",
        2: "根據照片內容生成一段引人注目的文案，吸引讀者的注意力，輸出文案就好",
        3: "根據照片內容輸出一段幽默且誇張的惡搞句子，輸出惡搞的句子就好",
        4: "根據照片內容創造一個笑話或諧音梗，讓人忍俊不禁，輸出笑話或諧音梗就好",
        5: "根據照片內容推測此人的性格，將其分類為某種動物並進行詳細分析，例如和善的人比喻成鴿子、漂亮的人比喻成蝴蝶、諸如此類，輸出分析結果就好",
        6: "把自己當作一個月老，如果在畫面中看到兩個人，幫我分析兩個人的適配度（0~100分)，並以“適配度xx分！！！”為開頭"
    }

    image_path = capture_image()
    if image_path:
        generated_contents = {}
        for key, prompt in prompts.items():
            generated_contents[key] = generate_content(image_path, prompt)
            formatted_content = format_text(generated_contents[key], line_length=30)
            output_file = f"static/content_{key}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted_content)
            print(f"內容 {key} 已生成並保存至：{output_file}")

        # 終端機只顯示選擇的文本
        if choice in generated_contents:
            print(f"\n您選擇的內容如下：\n{format_text(generated_contents[choice], line_length=30)}")
        else:
            print("無效選項，請輸入 1 到 6。")

if __name__ == "__main__":
    main()
