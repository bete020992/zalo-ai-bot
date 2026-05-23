from flask import Flask, request, jsonify
import requests
import os

# Token của bạn
ZALO_BOT_TOKEN = "24411053582055381:jhPyVSWiLZBGcJTwEUjydutgckIAfdaxjOtpGDMvYhxEvecIEuzvBzDpsoRCQSmj"
GEMINI_API_KEY = "AIzaSyAuAGX3J0eNkQN7dmMzHFMseQHPUBjAFlI"

# Gemini model ổn định hơn
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

app = Flask(__name__)

SYSTEM_PROMPT = """
Bạn là trợ lý AI cá nhân nói chuyện trên Zalo.

CÁCH TRẢ LỜI:
- Trả lời như người thật, tự nhiên, thông minh, không robot.
- Ngắn gọn nhưng đủ ý.
- Nếu câu hỏi đơn giản thì trả lời ngắn.
- Nếu câu hỏi cần giải thích thì giải thích dễ hiểu.
- Không nói lan man, không giáo điều.
- Nếu không biết thì nói không chắc, không bịa.
- Nói tiếng Việt tự nhiên.

PHONG CÁCH:
- Thông minh
- Hơi hài nhẹ
- Mặn mòi vừa phải
- Có cảm xúc như người thật
- Không trả lời ngáo

THÔNG TIN CHỦ:
Bạn đang hỗ trợ cho Lê Quốc Tài, 33 tuổi, quân nhân.
Cao 1m72, nặng 76kg.
Đam mê chạy bộ sub-2.
Dùng Apple Watch Ultra 2.
Đi giày Nike Pegasus, Novablast 5, Puma Deviate Nitro 3, giày SP3.
Không bao giờ nói Tài có giày Asics Magic Speed.

QUY TẮC:
- Nếu người dùng hỏi linh tinh thì trả lời tự nhiên như bạn bè.
- Nếu hỏi kiến thức thì trả lời chính xác.
- Nếu hỏi vui thì vui lại.
- Nếu người dùng chửi thì đáp tỉnh.
- Không được bịa chuyện.
"""

# Bộ nhớ đơn giản cho từng user
chat_memory = {}

def ask_gemini(user_id, user_message):
    history = chat_memory.get(user_id, [])

    history_text = ""
    for msg in history[-6:]:
        history_text += f"{msg}\n"

    full_prompt = f"""
{SYSTEM_PROMPT}

LỊCH SỬ CHAT:
{history_text}

User: {user_message}
AI:
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        res_data = response.json()

        if "candidates" in res_data:
            ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]

            history.append(f"User: {user_message}")
            history.append(f"AI: {ai_reply}")
            chat_memory[user_id] = history[-10:]

            return ai_reply

        elif "error" in res_data:
            error_msg = res_data["error"]["message"]

            if "quota" in error_msg.lower():
                return "Tôi đang bận chút 😄 hỏi lại sau 30 giây nhé."

            return "AI đang bận, thử lại sau."

        else:
            return "AI đang bận, thử lại sau."

    except Exception as e:
        return "Lỗi hệ thống."


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

        ai_reply = ask_gemini(sender_id, user_message)
        send_zalo_message(sender_id, ai_reply)

    except Exception as e:
        print("Webhook lỗi:", e)

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
