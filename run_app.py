import cv2
import math
import time
import threading
import winsound
from ultralytics import YOLO
import cvzone

# --- CẤU HÌNH QUAN TRỌNG ---
# Chọn nguồn: Để số 0 nếu dùng Webcam, hoặc điền tên file nếu dùng Video_Test/test5.mp4
INPUT_SOURCE = 0
# INPUT_SOURCE = 0 

MODEL_PATH = "best.pt"
CONF_THRESHOLD = 0.4   # tầm 0.2 cho video test, của cam thì để 0.4
ALERT_DELAY = 10        

# --- CẤU HÌNH ĐỘ NHẠY ---
FIRE_RATIO_THRESHOLD = 0.001 

alarm_playing = False
last_alert_time = 0      

# --- KẾT NỐI TELEGRAM ---
try:
    import my_telegram
    print("✅ Đã kết nối module Telegram")
except:
    print("⚠️ Không có file my_telegram.py, bỏ qua gửi tin.")

def play_alarm_sound():
    global alarm_playing
    if not alarm_playing:
        alarm_playing = True
        try:
            for _ in range(5):
                winsound.Beep(2000, 200) 
        except:
            pass
        finally:
            alarm_playing = False

# Load Model
print("⏳ Đang nạp model...")
try:
    model = YOLO(MODEL_PATH)
    classNames = model.names 
    print(f"✅ Model OK. Lớp: {classNames}")
except:
    model = YOLO("yolov8n.pt")
    classNames = model.names
    print("⚠️ Dùng model mặc định.")

# Khởi tạo Video/Camera
cap = cv2.VideoCapture(INPUT_SOURCE)

# --- BƯỚC TÍNH TOÁN NGƯỠNG TỰ ĐỘNG ---
ret, frame = cap.read()
if ret:
    frame_height, frame_width, _ = frame.shape
    total_pixels = frame_width * frame_height
    dynamic_area_threshold = int(total_pixels * FIRE_RATIO_THRESHOLD)
    
    print(f"\n🖥️ Kích thước Video: {frame_width}x{frame_height}")
    print(f"🔥 Ngưỡng báo động (0.1%): > {dynamic_area_threshold} pixels")
else:
    print("❌ Lỗi: Không mở được Video/Camera!")
    exit()

# Reset video về đầu
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

while True:
    success, img = cap.read()
    if not success: 
        # Nếu là Video thì cho lặp lại liên tục để Demo
        if isinstance(INPUT_SOURCE, str):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        else:
            break

    # Nếu video quá to (4K), resize ảnh hiển thị cho vừa màn hình laptop
    display_img = img.copy() 
    
    # --- CHỈNH SỬA Ở ĐÂY: Dùng imgsz= 640 cho cam ---// 1180 cho video test
    results = model(img, stream=True, imgsz=640, conf=CONF_THRESHOLD, verbose=False)
    
    status_text = "AN TOAN"
    status_color = (0, 255, 0) 
    frame_has_fire = False 

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            area = w * h
            
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            
            if isinstance(classNames, dict):
                classNameRaw = classNames[cls]
            else:
                classNameRaw = classNames[cls]
            
            name_lower = str(classNameRaw).lower()
            is_fire = ("fire" in name_lower) or ("smoke" in name_lower)

            # LOGIC QUYẾT ĐỊNH
            if is_fire:
                
                # Tính % diện tích lửa so với toàn màn hình
                fire_percentage = (area / total_pixels) * 100
                
                if area > dynamic_area_threshold:
                    frame_has_fire = True
                    
                    # Vẽ khung đỏ đậm
                    cvzone.cornerRect(display_img, (x1, y1, w, h), colorR=(0, 0, 255), t=4)
                    
                    # Hiện thông số % lửa
                    info_text = f"CHAY! {fire_percentage:.2f}%"
                    cvzone.putTextRect(display_img, info_text, (max(0, x1), max(35, y1)), scale=1.5, thickness=2, colorR=(0,0,255))
                    
                    # 1. Hú còi
                    if not alarm_playing:
                        threading.Thread(target=play_alarm_sound).start()

                    # 2. Gửi Telegram
                    if time.time() - last_alert_time > ALERT_DELAY:
                        last_alert_time = time.time()
                        print("🚀 ĐANG GỬI TIN NHẮN TELEGRAM...")
                        try:
                            msg = f"CẢNH BÁO KHẨN CẤP: Phát hiện lửa! (Độ lớn: {fire_percentage:.2f}%)"
                            threading.Thread(target=my_telegram.send_alert, args=(msg,)).start()
                        except:
                            pass
                else:
                    # Lửa siêu nhỏ (nhỏ hơn 0.1%) -> Vẽ màu vàng cảnh báo sớm
                    cvzone.cornerRect(display_img, (x1, y1, w, h), colorR=(0, 255, 255), t=2)

    # Cập nhật trạng thái hiển thị
    if frame_has_fire:
        cv2.rectangle(display_img, (0, 0), (1280, 80), (0, 0, 255), -1) 
        cv2.putText(display_img, "NGUY HIEM! CHAY!", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
    else:
        cv2.rectangle(display_img, (0, 0), (1280, 80), (0, 255, 0), -1)
        cv2.putText(display_img, "AN TOAN", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

    # Resize cửa sổ hiển thị nếu video quá to
    if frame_width > 1500:
        display_img = cv2.resize(display_img, (1280, 720))

    cv2.imshow("Smart Fire Alert System v2.0", display_img)

    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()