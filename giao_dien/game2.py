import tkinter as tk
from tkinter import messagebox
import random
import pygame
import os
import time

# **************************************************
# MÔ PHỎNG LỚP SERIALDATA (Dùng chung từ trò chơi trước)
# **************************************************
class SerialData:
    def __init__(self):
        self.attention = 0
        self.max_attention = 0 
        self.poor_signal = 0 

ReadSerial = SerialData() 
# **************************************************

# --- CẤU HÌNH TRÒ CHƠI ---
GO_COLOR_SPACE = "blue"   # Xanh -> Nhấn Space (Tín hiệu Go 1)
GO_COLOR_ENTER = "red"    # Đỏ -> Nhấn Enter (Tín hiệu Go 2)

COLORS = [GO_COLOR_SPACE, GO_COLOR_ENTER]

INTERVAL_MIN_MS = 1000  # Thời gian tối thiểu giữa các lần xuất hiện
INTERVAL_MAX_MS = 2000  # Thời gian tối đa giữa các lần xuất hiện
MAX_TRIALS = 40         # Tổng số lần thử (lượt)

ATTENTION_UPDATE_MS = 100 # Cập nhật hiển thị Attention

# --- CẤU HÌNH GIAO DIỆN ĐÃ SỬA ---
CIRCLE_SIZE = 200 # ĐÃ SỬA: Đường kính chấm tròn (từ 100px lên 200px)
FADE_TIME_MS = 200 # Thời gian hiệu ứng Fade

# --- KHỞI TẠO PYGAME CHO ÂM THANH ---
SOUND_DIR = "sounds"

try:
    pygame.mixer.init()
    SOUND_CORRECT = pygame.mixer.Sound(os.path.join(SOUND_DIR, "ding.mp3"))
    SOUND_INCORRECT = pygame.mixer.Sound(os.path.join(SOUND_DIR, "buzz.mp3"))
    SOUND_CORRECT_PLAY = lambda: SOUND_CORRECT.play()
    SOUND_INCORRECT_PLAY = lambda: SOUND_INCORRECT.play()
except pygame.error as e:
    print(f"Lỗi Pygame/âm thanh: {e}")
    SOUND_CORRECT_PLAY = lambda: print("DING!") 
    SOUND_INCORRECT_PLAY = lambda: print("BUZZ!") 

# --- BIẾN LƯU TRỮ TRẠNG THÁI ---
game_running = False
current_trial = 0
current_color = None
timer_id = None
time_start = 0 

# --- KẾT QUẢ TEST ---
rt_list = []      
hit_count = 0     
miss_count = 0    
error_count = 0   

# --- THIẾT LẬP GIAO DIỆN TKINTER ---
root = tk.Tk()
root.title("Phân Biệt Tín Hiệu: Xanh/Đỏ")
root.attributes('-fullscreen', True) 
root.config(bg="black")

# Nhãn hiển thị ATTENTION (Góc trái trên cùng)
attention_label = tk.Label(root, text="Attention: N/A", font=("Arial", 20, "bold"), 
                           fg="cyan", bg="black", anchor='nw')
attention_label.place(x=10, y=10)

# Vùng chứa Canvas cho hình tròn
center_frame = tk.Frame(root, bg="black")
center_frame.pack(expand=True)
# Kích thước Canvas ban đầu để chứa luật chơi (tăng nhẹ theo font mới)
canvas = tk.Canvas(center_frame, width=700, height=400, bg="black", highlightthickness=0)
canvas.pack()

# Nút BẮT ĐẦU (ĐÃ SỬA kích thước chữ)
start_button = tk.Button(root, text="BẮT ĐẦU", font=("Arial", 40, "bold"), 
                         fg="white", bg="#4CAF50", padx=20, pady=10, 
                         command=lambda: start_game(None))
start_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

# Nhãn hiển thị trạng thái và hướng dẫn
status_label = tk.Label(root, text="", font=("Arial", 28), fg="white", bg="black")
status_label.pack(side=tk.BOTTOM, pady=50)

# --- CÁC HÀM TÍCH HỢP ATTENTION ---

def update_attention_display():
    """Hàm cập nhật hiển thị Attention (gọi mỗi 100ms)."""
    current_attention = ReadSerial.attention
    
    if game_running and current_attention > ReadSerial.max_attention:
         ReadSerial.max_attention = current_attention
         
    if game_running:
        attention_label.config(text=f"Attention: {current_attention}/100")
    else:
        attention_label.config(text="Attention: N/A")

    root.after(ATTENTION_UPDATE_MS, update_attention_display)

# --- CÁC HÀM TRÒ CHƠI ---

def get_next_color():
    """Chọn ngẫu nhiên màu Xanh hoặc Đỏ."""
    return random.choice(COLORS)

def start_trial():
    """Xuất hiện tín hiệu (màu) và bắt đầu đếm thời gian."""
    global current_color, time_start, current_trial, timer_id

    if not game_running: return

    # 1. Kiểm tra giới hạn lượt
    if current_trial >= MAX_TRIALS:
        stop_game(is_finished=True)
        return

    current_trial += 1
    
    # 2. Tạo màu mới và hiển thị
    current_color = get_next_color()
    
    canvas.delete("all")
    
    # Vẽ hình tròn mới (Fade-in)
    canvas.create_oval(0, 0, CIRCLE_SIZE, CIRCLE_SIZE, fill=current_color, tags="circle")
    
    # 3. Ghi nhận thời điểm bắt đầu
    time_start = time.time()
    
    # 4. Cập nhật trạng thái
    action = "SPACE" if current_color == GO_COLOR_SPACE else "ENTER"
    status_label.config(text=f"Lượt: {current_trial}/{MAX_TRIALS} | Tín hiệu {current_color.upper()}! Nhấn {action}!")
    
    # 5. Đặt hẹn giờ để kết thúc lượt chơi
    random_interval = random.randint(INTERVAL_MIN_MS, INTERVAL_MAX_MS)
    timer_id = root.after(random_interval, end_trial)

def end_trial():
    """Ẩn tín hiệu, ghi nhận bỏ lỡ (Miss) và chuyển lượt."""
    global current_color, timer_id, miss_count

    if not game_running: return

    # 1. Xóa tín hiệu (Fade-out)
    canvas.delete("all")
    
    # 2. Ghi nhận bỏ lỡ (Miss)
    if current_color is not None:
        miss_count += 1
        SOUND_INCORRECT_PLAY()
        status_label.config(text=f"Lượt: {current_trial}/{MAX_TRIALS} | ❌ BỎ LỠ! (+{miss_count} Miss)")
    
    current_color = None 

    # 3. Bắt đầu lượt mới sau FADE_TIME_MS (tạo khoảng nghỉ)
    timer_id = root.after(FADE_TIME_MS, start_trial)


def handle_keypress(event):
    """Xử lý sự kiện nhấn phím Space hoặc Enter."""
    global current_color, hit_count, error_count, time_start, rt_list, game_running

    pressed_key = event.keysym

    if not game_running and pressed_key == 'Return':
        start_game(None)
        return

    if not game_running or current_color is None:
        if current_color is None and (pressed_key == 'space' or pressed_key == 'Return'):
             error_count += 1
             SOUND_INCORRECT_PLAY()
             status_label.config(text=f"Lượt: {current_trial}/{MAX_TRIALS} | ❌ NHẤN THỪA! (+{error_count} Lỗi)")
        return

    if pressed_key not in ['space', 'Return']:
        return

    if timer_id:
        root.after_cancel(timer_id)

    time_end = time.time()
    reaction_time = (time_end - time_start) * 1000 
    
    is_correct = False
    
    if current_color == GO_COLOR_SPACE and pressed_key == 'space':
        is_correct = True
    elif current_color == GO_COLOR_ENTER and pressed_key == 'Return':
        is_correct = True

    if is_correct:
        hit_count += 1
        rt_list.append(reaction_time)
        SOUND_CORRECT_PLAY()
        status_label.config(text=f"Lượt: {current_trial}/{MAX_TRIALS} | ✔️ HIT! RT: {reaction_time:.2f}ms")
        
    else:
        error_count += 1
        SOUND_INCORRECT_PLAY()
        status_label.config(text=f"Lượt: {current_trial}/{MAX_TRIALS} | ❌ LỖI PHÍM! (+{error_count} Lỗi)")

    # Xóa tín hiệu sau phản ứng
    canvas.delete("all")
    current_color = None

    if game_running:
        root.after(FADE_TIME_MS, start_trial)

def show_start_screen():
    """Hiển thị màn hình bắt đầu với luật chơi."""
    canvas.config(width=700, height=400) # Cập nhật kích thước canvas
    canvas.delete("all")
    
    rule_text = (
        "LUẬT CHƠI\n\n"
        "1. XANH (Blue) → Nhấn: SPACE\n"
        "2. ĐỎ (Red)   → Nhấn: ENTER\n\n"
        "Mục tiêu: Phản ứng nhanh và chính xác!\n"
    )
    
    # ĐÃ SỬA: Tăng kích thước font luật chơi
    canvas.create_text(350, 200, text=rule_text, fill="white", 
                       font=("Arial", 36, "bold"), tags="info", justify='center')
    
    status_label.config(text="")
    start_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
    canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def start_game(event):
    """Thiết lập các biến và bắt đầu vòng lặp game."""
    global game_running, current_trial, hit_count, miss_count, error_count, rt_list
    global current_color, timer_id, time_start
    
    if game_running: return

    # Ẩn nút Start
    start_button.place_forget() 

    # Reset biến
    game_running = True
    current_trial = 0
    hit_count = miss_count = error_count = 0
    rt_list = []
    current_color = None
    ReadSerial.max_attention = ReadSerial.attention 
    
    # Cài đặt Canvas cho chế độ game (kích thước hình tròn)
    canvas.config(width=CIRCLE_SIZE, height=CIRCLE_SIZE)
    canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER) # Đặt canvas ở giữa

    if attention_label.cget("text") == "Attention: N/A":
        update_attention_display() 

    status_label.config(text=f"Lượt: 0/{MAX_TRIALS} | Chuẩn bị...")
    
    if timer_id: root.after_cancel(timer_id)
    timer_id = root.after(1000, start_trial)


def stop_game(is_finished=False):
    """Dừng trò chơi và hiển thị kết quả tổng hợp."""
    global game_running, timer_id
    game_running = False
    
    if timer_id: root.after_cancel(timer_id)
    
    canvas.delete("all")
    
    # Tính toán kết quả
    avg_rt = sum(rt_list) / len(rt_list) if rt_list else 0
    total_error = miss_count + error_count
    
    # Thông báo kết quả
    max_att_msg = f"Max Attention Đạt Được: {ReadSerial.max_attention}"
    
    result_message = (
        f"✅ HOÀN THÀNH {current_trial} LƯỢT!\n\n"
        f"1. Tốc độ (Avg RT): {avg_rt:.2f} ms\n"
        f"2. Hit (Đúng): {hit_count} lần\n"
        f"3. Tổng Lỗi (Miss + Error): {total_error} lần\n"
        f"   - Miss (Bỏ lỡ): {miss_count} lần\n"
        f"   - Error (Sai phím/Nhấn thừa): {error_count} lần\n\n"
        f"{max_att_msg}"
    )
    
    messagebox.showinfo("Kết quả Test", result_message)

    show_start_screen() 

def close_game(event):
    """Đóng cửa sổ."""
    root.destroy()

# --- GÁN SỰ KIỆN PHÍM TẮT ---
root.bind('<space>', handle_keypress) 
root.bind('<Return>', handle_keypress) 
root.bind('<Escape>', close_game)    

# Khởi tạo màn hình chờ
show_start_screen()

# Chạy giao diện
root.mainloop()