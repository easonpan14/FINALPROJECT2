from flask import Flask, render_template, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    # 獲取圖片路徑
    image_url = url_for('static', filename='image1.jpg')
    
    # 讀取詩句內容
    poem_path = os.path.join('static', 'poem.txt')
    if os.path.exists(poem_path):
        with open(poem_path, "r") as f:
            poem = f.read()
    else:
        poem = "詩句尚未生成"

    return render_template('index.html', poem=poem, image_url=image_url)

if __name__ == '__main__':
    print("伺服器啟動中，請使用伺服器 IP 地址訪問")
    app.run(debug=True, host='0.0.0.0', port=5001)
