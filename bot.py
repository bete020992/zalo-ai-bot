from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import os

# Cấu hình
ZALO_BOT_TOKEN = "24411053582055381:jhPyVSWiLZBGcJTwEUjydutgckIAfdaxjOtpGDMvYhxEvecIEuzvBzDpsoRCQSmj"
GEMINI_API_KEY = "AIzaSyAuAGX3J0eNkQN7dmMzHFMseQHPUBjAFlI"

genai.configure(api_key=GEMINI_API_KEY)

# Sử dụng gemini-pro để tránh lỗi 404 với flash trên một số key
model = genai.GenerativeModel('gemini-pro')

SYSTEM_PROMPT = """Bạn là trợ lý ảo của Lê Quốc Tài, 33 tuổi, quân nhân. Hãy trả lời ngắn gọn, súc tích. Tài cao 1m72, nặng 76kg, đam mê chạy bộ sub-2, dùng Apple Watch Ultra 2, đi giày Nike Pegasus, Novablast 5, Puma Deviate Nitro 3, Giày sp3. Tuyệt đối không có giày Asics Magic Speed."""

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or "event_name" not in data: return jsonify({"status": "ok"}), 200
    
    sender_id = data["message"]["chat"]["id"]
    user_message = data["message"]["text"]
    
    try:
        response = model.generate_content(SYSTEM_PROMPT + "\nUser hỏi: " + user_message)
        ai_reply = response.text
    except Exception as e:
        ai_reply = "Lỗi hệ thống: " + str(e)
    
    requests.post(f"https://bot-api.zapps.me/bot{ZALO_BOT_TOKEN}/sendMessage", 
                  json={"chat_id": sender_id, "text": ai_reply})
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
