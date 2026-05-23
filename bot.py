from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import os # Thêm dòng này

ZALO_BOT_TOKEN = "24411053582055381:jhPyVSWiLZBGcJTwEUjydutgckIAfdaxjOtpGDMvYhxEvecIEuzvBzDpsoRCQSmj"
GEMINI_API_KEY = "AIzaSyCqjp9FFzs2A5ntXEF6VJ2a2Cy-zuMJL5Y"

genai.configure(api_key=GEMINI_API_KEY)

# Tự dò tìm model khả dụng
def get_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except:
        pass
    return None

model = get_model()

SYSTEM_PROMPT = """Bạn là trợ lý ảo của Lê Quốc Tài, 33 tuổi, quân nhân. Hãy trả lời ngắn gọn, súc tích (dưới 2000 ký tự). Tài cao 1m72, nặng 76kg, đam mê chạy bộ sub-2, dùng Apple Watch Ultra 2, đi giày Nike Pegasus, Novablast 5, Puma Deviate Nitro 3, Giày sp3. Tuyệt đối không có giày Asics Magic Speed."""

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and data.get("event_name") == "message.text.received":
        sender_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        
        try:
            if model:
                response = model.generate_content(SYSTEM_PROMPT + "\nUser hỏi: " + user_message)
                ai_reply = response.text
            else:
                ai_reply = "Lỗi: Không tìm thấy model AI nào khả dụng."
            
            if len(ai_reply) > 2000: ai_reply = ai_reply[:1990] + "..."
        except Exception as e:
            ai_reply = "Lỗi hệ thống: " + str(e)
        
        requests.post(f"https://bot-api.zapps.me/bot{ZALO_BOT_TOKEN}/sendMessage", 
                      json={"chat_id": sender_id, "text": ai_reply})
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Dòng này cực kỳ quan trọng:
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
