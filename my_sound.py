import threading
import winsound
import time

def play_siren():
    """Hàm này phát tiếng kêu TÍT TÍT liên tục"""
    # Chạy trong luồng riêng (Thread) để không làm đơ camera
    thread = threading.Thread(target=_run_sound)
    thread.start()

def _run_sound():
    print("🔊 LOA: O e O e... (Đang báo động!)")
    try:
        # Kêu 5 lần liên tiếp
        for _ in range(5): 
            # Beep(tần số Hz, thời gian ms)
            winsound.Beep(1000, 500) # Tít...
            winsound.Beep(1500, 300) # Tít!
    except Exception as e:
        print(f"Lỗi âm thanh: {e}")

# --- PHẦN TEST (Chạy thử file này để xem loa có kêu không) ---
if __name__ == "__main__":
    print("Bắt đầu test loa...")
    play_siren()
    print("Xong lệnh phát loa (Code vẫn chạy tiếp, không bị đơ!)")