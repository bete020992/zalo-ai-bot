from flask import Flask, request, jsonify
import requests
import google.generativeai as genai

ZALO_BOT_TOKEN = "24411053582055381:jhPyVSWiLZBGcJTwEUjydutgckIAfdaxjOtpGDMvYhxEvecIEuzvBzDpsoRCQSmj"
GEMINI_API_KEY = "AIzaSyCqjp9FFzs2A5ntXEF6VJ2a2Cy-zuMJL5Y"

genai.configure(api_key=GEMINI_API_KEY)

# --- ĐÂY LÀ PHẦN BƠM KÝ ỨC CỐT LÕI CHO AI ---
SYSTEM_PROMPT = """Bạn là trợ lý ảo cá nhân thân thiết và huấn luyện viên AI riêng của tôi.
Hãy luôn trả lời ngắn gọn, súc tích (dưới 2000 ký tự) và trò chuyện bằng tiếng Việt một cách tự nhiên, mặn mòi, gần gũi.
Dưới đây là thông tin mặc định về tôi (người đang chat với bạn), hãy ghi nhớ kỹ để tư vấn cho chính xác:
- Tên của tôi: Lê Quốc Tài, 33 tuổi, Nam.
- Nghề nghiệp: Quân nhân công tác trong quân đội (thường xuyên có các hoạt động thể lực, hành quân).
- Thể chất: Cao 1m72, nặng 76kg.
- Đam mê & Mục tiêu: Chạy bộ đường dài (cả chạy road và cày trail). Đang nỗ lực tập luyện ép pace để đạt mục tiêu hoàn thành giải chạy với thành tích Sub-2.
- Đồ công nghệ: Đang đeo Apple Watch Ultra 2, luôn đồng bộ dữ liệu chạy bộ lên Strava và Nike Run Club (NRC).
- Giày đang đi: Nike Pegasus, Novablast 5, Puma Deviate Nitro 3 và Giày sp3. (Lưu ý: Tôi KHÔNG CÓ giày Asics Magic Speed, đừng bao giờ nhầm lẫn khuyên tôi mang đôi đó).
Khi tôi hỏi về thể lực, bài tập hay thiết bị, hãy dựa vào dữ liệu cơ thể và thói quen này để phân tích như một người đã theo dõi tôi từ lâu."""

try:
    available_models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    chosen_model = available_models[0] if available_models else "gemini-1.5-flash"
except Exception as e:
    chosen_model = "gemini-1.5-flash"

print("=== Bot đang dùng bộ não của:", chosen_model, "===")

# Nhúng bộ nhớ vào AI
model = genai.GenerativeModel(
    model_name=chosen_model,
    system_instruction=SYSTEM_PROMPT
)

app = Flask(__name__)

def send_zalo_message(chat_id, text):
    url = f"https://bot-api.zapps.me/bot{ZALO_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    res = requests.post(url, json=payload)
    print("Trạng thái AI trả lời Zalo:", res.text)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Có tin nhắn từ Zalo:", data)
    
    if data and data.get("event_name") == "message.text.received":
        sender_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        
        try:
            response = model.generate_content(user_message)
            ai_reply = response.text
            
            if len(ai_reply) > 2000:
                ai_reply = ai_reply[:1990] + "..."
                
        except Exception as e:
            ai_reply = "Lỗi kết nối AI: " + str(e)
        
        send_zalo_message(sender_id, ai_reply)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=8080)
