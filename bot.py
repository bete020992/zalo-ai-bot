from flask import Flask, request, jsonify
import requests
import os

# Token và API key của bạn
ZALO_BOT_TOKEN = "24411053582055381:jhPyVSWiLZBGcJTwEUjydutgckIAfdaxjOtpGDMvYhxEvecIEuzvBzDpsoRCQSmj"
GEMINI_API_KEY = "AIzaSyAuAGX3J0eNkQN7dmMzHFMseQHPUBjAFlI"

# Gemini model mới (đã sửa lỗi 404)
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

app = Flask(__name__)

SYSTEM_PROMPT = """
Bạn là trợ lý ảo của Lê Quốc Tài, 33 tuổi, quân nhân.
Tài cao 1m72, nặng 76kg, đam mê chạy bộ sub-2.
Dùng Apple Watch Ultra 2.
Đi giày Nike Pegasus, Novablast 5, Puma Deviate Nitro 3, Giày sp3.
Không bao giờ nói Tài có giày Asics Magic Speed.
Trả lời ngắn gọn, mặn mòi.
"""

def ask_gemini(user_message):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT + "\n\nUser hỏi: " + user_message
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        res_data = response.json()

        if "candidates" in res_data:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in res_data:
            return "Lỗi Gemini: " + res_data["error"]["message"]
        else:
            return "Gemini không trả dữ liệu."

    except Exception as e:
        return "Lỗi hệ thống: " + str(e)


def send_zalo_message(chat_id, text):
    url = f"https://bot-api.zapps.me/bot{ZALO_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Lỗi gửi Zalo:", e)


@app.route('/')
def home():
    return "Bot đang chạy OK"


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if not data or "message" not in data:
        return jsonify({"status": "ok"}), 200

    try:
        sender_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        ai_reply = ask_gemini(user_message)
        send_zalo_message(sender_id, ai_reply)

    except Exception as e:
        print("Webhook lỗi:", e)

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
