import time
import requests

BOT_TOKEN = "8920477645:AAEzi5AEGhmbO2GIcW83x9CCTEfSvL9sbLo"
CHANNEL_USERNAME = "@Evalex_academy"
CHANNEL_LINK = "https://t.me/Evalex_academy"
EXAM_LINK = "https://exam-frontend-m8id.vercel.app"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

def answer_callback(callback_query_id, text, show_alert=False):
    payload = {"callback_query_id": callback_query_id, "text": text, "show_alert": show_alert}
    requests.post(f"{BASE_URL}/answerCallbackQuery", json=payload)

def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/editMessageText", json=payload)

def is_subscribed(user_id):
    url = f"{BASE_URL}/getChatMember"
    try:
        response = requests.get(url, params={"chat_id": CHANNEL_USERNAME, "user_id": user_id}, timeout=10).json()
        if response.get("ok"):
            return response["result"]["status"] in ["creator", "administrator", "member"]
    except Exception as e:
        print("Subscription check error:", e)
    return False

def build_join_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📢 Join Evalex Academy", "url": CHANNEL_LINK}],
            [{"text": "🔄 Verify Membership", "callback_data": "check_membership"}]
        ]
    }

def build_exam_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🚀 Open Examination Portal", "url": EXAM_LINK}]
        ]
    }

def main():
    print("Bot is active on Railway...")
    offset = 0
    while True:
        try:
            updates = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35).json()
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_id = update["message"]["from"]["id"]
                        if update["message"]["text"] == "/start":
                            if is_subscribed(user_id):
                                send_message(chat_id, "✅ **Membership verified!** Click below to launch your exam:", reply_markup=build_exam_keyboard())
                            else:
                                send_message(chat_id, "⚠️ You must join **Evalex Academy** to access the exam.", reply_markup=build_join_keyboard())

                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        cq_id = cq["id"]
                        user_id = cq["from"]["id"]
                        chat_id = cq["message"]["chat"]["id"]
                        message_id = cq["message"]["message_id"]

                        if cq.get("data") == "check_membership":
                            if is_subscribed(user_id):
                                answer_callback(cq_id, "✅ Membership verified!")
                                edit_message(chat_id, message_id, "✅ **Channel membership verified!** Click below to start:", reply_markup=build_exam_keyboard())
                            else:
                                answer_callback(cq_id, "❌ You haven't joined @Evalex_academy yet!", show_alert=True)
        except Exception as e:
            print(f"Network error encounter: {e}. Retrying in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    main()
