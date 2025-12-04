import requests

# --- CẤU HÌNH ---
# Token lấy từ @BotFather sau khi tạo bot Telegram
BOT_TOKEN = "8260819988:AAELfs4nMho0mpn8KNiNLu-HX2k0QzibeqI"

#   Chat ID của người nhận
CHAT_ID = "5791634913" 

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": "🔥 " + message
        }
        requests.post(url, data=data)
        print("✅ Đã gửi tin nhắn Telegram thành công!")
    except Exception as e:
        print(f"❌ Lỗi gửi tin: {e}")

# --- TEST THỬ ---
if __name__ == "__main__":
    print("Đang gửi thử tin nhắn...")
    if CHAT_ID == "DÁN_ID_CỦA_BẠN_VÀO_ĐÂY":
        print("❌ QUÊN DÁN CHAT ID RỒI KÌA BẠN ƠI!")
    else:
        send_alert("Cảnh báo: Hệ thống Báo cháy Nhóm 4 xin chào!")