from flask import Flask, render_template, url_for, request, redirect, flash
import os
from werkzeug.utils import secure_filename

# Flask 應用設定
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於 flash 訊息
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 確保上傳目錄存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """檢查文件是否為允許的圖片類型"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    content_type = request.form.get('content_type', '1')  # 預設為生成詩句
    content_file = f"static/content_{content_type}.txt"
    
    # 獲取圖片路徑，添加版本參數
    image_path = 'static/image1.jpg'
    if os.path.exists(image_path):
        image_url = url_for('static', filename='image1.jpg', v=str(os.path.getmtime(image_path)))
    else:
        image_url = None

    # 讀取對應內容文件
    if os.path.exists(content_file):
        with open(content_file, "r", encoding="utf-8") as f:
            content = f.read().strip()  # 清理多餘空白與換行
    else:
        content = "內容尚未生成，請先執行生成功能"

    return render_template('index.html', content=content, image_url=image_url, selected_type=content_type)

@app.route('/upload', methods=['POST'])
def upload():
    """處理用戶上傳圖片"""
    if 'file' not in request.files:
        flash('未找到文件')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('未選擇文件')
        return redirect('/')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        flash('圖片上傳成功！')
        return redirect('/')
    else:
        flash('文件格式不支持，請上傳 jpg/jpeg/png 格式的圖片')
        return redirect('/')

@app.route('/share/<content_type>')
def share(content_type):
    """分享功能：生成社交媒體分享鏈接"""
    content_file = f"static/content_{content_type}.txt"
    if os.path.exists(content_file):
        with open(content_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # URL 編碼
        share_url = f"https://twitter.com/intent/tweet?text={content}"
        return redirect(share_url)
    else:
        flash('無法分享，內容尚未生成')
        return redirect('/')

if __name__ == '__main__':
    print("伺服器啟動中，請使用伺服器 IP 地址訪問")
    app.run(debug=True, host='0.0.0.0', port=5001)
