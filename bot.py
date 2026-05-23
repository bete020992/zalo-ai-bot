from flask import Flask, request, jsonify
import requests
import os

ZALO_BOT_TOKEN = "24411053582055381:jhPyVSWiLZBGcJTwEUjydutgckIAfdaxjOtpGDMvYhxEvecIEuzvBzDpsoRCQSmj"
GEMINI_API_KEY = "AIzaSyAuAGX3J0eNkQN7dmMzHFMseQHPUBjAFlI"
# Đổi từ v1beta sang v1
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

app = Flask(__name__)

SYSTEM_PROMPT = "Bạn là trợ lý ảo của Lê Quốc Tài, 33 tuổi, quân nhân. Tài cao 1m72, nặng 76kg, đam mê chạy bộ sub-2, dùng Apple Watch Ultra 2, đi giày Nike Pegasus, Novablast 5, Puma Deviate Nitro 3, Giày sp3. Không bao giờ nói Tài có giày Asics Magic Speed. Trả lời ngắn gọn, mặn mòi."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or "event_name" not in data: return jsonify({"status": "ok"}), 200
    
    sender_id = data["message"]["chat"]["id"]
    user_message = data["message"]["text"]
    
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\nUser hỏi: " + user_message}]}]
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        res_data = response.json()
        
        if "candidates" in res_data:
            ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # In ra lỗi cụ thể để biết nó là gì
            ai_reply = "Lỗi API: " + str(res_data)
            
    except Exception as e:
        ai_reply = "Lỗi hệ thống: " + str(e)
    
    requests.post(f"https://bot-api.zapps.me/bot{ZALO_BOT_TOKEN}/sendMessage", 
                  json={"chat_id": sender_id, "text": ai_reply})
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
