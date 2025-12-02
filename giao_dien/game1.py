# import ReadSerial
# poor = ReadSerial.poor
# attention = ReadSerial.attention
# meditation = ReadSerial.meditation
# print("poor:", poor)
# print("attention:", attention)
# print("meditation:", meditation)
# def check_connect():
#     connect = 0
#     if(poor == -1 and attention == -1 and meditation == -1):
#         print("check connect bluetooth")
#         connect = -1
#     elif(poor == 200):
#         print("check fting")
#         connect = -2
#     else:
#         connect = 1
#     return connect
# check_connect()
import tkinter as tk
from tkinter import messagebox
import random
import pygame
import os

# --- CẤU HÌNH TRÒ CHƠI ---
WORD_COLOR_MAP = {
    "ĐỎ": "red",
    "XANH": "blue",
    "VÀNG": "yellow",
    "TÍM": "purple"
}
WORDS = list(WORD_COLOR_MAP.keys())
COLORS = list(WORD_COLOR_MAP.values())

INTERVAL_MS = 1000  # Thời gian cho mỗi lần chọn (1 giây)
MAX_ROUNDS = 20     # Số lần được chọn tối đa (20 lượt)
SCORE_LIMIT = -3    # ĐIỂM GIỚI HẠN: Game Over nếu score <= -3
ATTENTION_UPDATE_MS = 100 # Thời gian cập nhật hiển thị Attention

# --- KHỞI TẠO PYGAME CHO ÂM THANH ---
SOUND_DIR = "sounds"

try:
    pygame.mixer.init()
    SOUND_CORRECT = pygame.mixer.Sound(os.path.join(SOUND_DIR, r"E:\arduino\mindway_mobile\giao_dien\sounds\ding.mp3"))
    SOUND_INCORRECT = pygame.mixer.Sound(os.path.join(SOUND_DIR, r"E:\arduino\mindway_mobile\giao_dien\sounds\buzz.mp3"))
    SOUND_CORRECT_PLAY = lambda: SOUND_CORRECT.play()
    SOUND_INCORRECT_PLAY = lambda: SOUND_INCORRECT.play()
except pygame.error as e:
    print(f"Lỗi Pygame/âm thanh: {e}")
    SOUND_CORRECT_PLAY = lambda: print("DING!") 
    SOUND_INCORRECT_PLAY = lambda: print("BUZZ!") 

# --- BIẾN LƯU TRỮ TRẠNG THÁI ---
current_word = "" 
current_color = ""
game_running = False
score = 0
current_round = 0 
timer_id = None 
last_match_state = False 
input_received = False 

# --- THIẾT LẬP GIAO DIỆN TKINTER ---
root = tk.Tk()
root.title("Stroop Test: Kiểm soát Thùy Trán")
root.geometry("800x600")
#root.attributes('-fullscreen', True) 
root.config(bg="black")

# Nhãn hiển thị ATTENTION (Góc trái trên cùng)
attention_label = tk.Label(root, text="Attention: N/A", font=("Arial", 20, "bold"), 
                           fg="cyan", bg="black", anchor='nw')
attention_label.place(x=10, y=10) # Đặt ở góc trái trên cùng

word_label = tk.Label(root, text="BẮT ĐẦU", font=("Arial", 180, "bold"), 
                      bg="black", fg="white", pady=100)
word_label.pack(expand=True)

score_label = tk.Label(root, text=f"Điểm: 0 | Lượt: 0/{MAX_ROUNDS} | Nhấn Space khi MÀU CHỮ = NGHĨA", 
                       font=("Arial", 24), fg="white", bg="black")
score_label.pack(side=tk.BOTTOM, pady=50)

# --- CÁC HÀM TÍCH HỢP ATTENTION ---




# --- CÁC HÀM TRÒ CHƠI ---

def get_new_stimulus():
    """Tạo ngẫu nhiên một Từ và Màu chữ."""
    word = random.choice(WORDS)
    color_name = random.choice(COLORS)
    return word, color_name

def is_match(word, color):
    """Kiểm tra xem Nghĩa của Từ có trùng với Màu chữ không."""
    if not word or word not in WORD_COLOR_MAP: return False
    return WORD_COLOR_MAP[word] == color

def update_score(change, message=""):
    """Cập nhật điểm số và kiểm tra giới hạn."""
    global score
    score += change
    score_label.config(text=f"Điểm: {score} | Lượt: {current_round}/{MAX_ROUNDS} | {message}")
    
    # Kiểm tra điều kiện Game Over
    if score <= SCORE_LIMIT:
        stop_game(is_finished=False, reason="SCORE_LIMIT")
        return True 
    return False 

def handle_miss():
    """Xử lý bỏ lỡ Match: trừ 1 điểm và kiểm tra Game Over."""
    SOUND_INCORRECT_PLAY()
    update_score(-1, "❌ Bỏ lỡ (Match)! -1 Điểm.")

def handle_timeout():
    global last_match_state, input_received
    if last_match_state and not input_received:
        handle_miss()

def update_word():
    global current_word, current_color, timer_id, current_round, last_match_state, input_received

    if not game_running: return

    # --- 1. Xử lý kết quả của lượt chơi ĐÃ QUA ---
    if current_round > 0:
        handle_timeout() 
        if not game_running: return # Dừng nếu Game Over do điểm âm

    # --- 2. Kiểm tra giới hạn lượt chơi ---
    if current_round >= MAX_ROUNDS:
        stop_game(is_finished=True)
        return

    # --- 3. Bắt đầu lượt chơi MỚI ---
    current_round += 1
    input_received = False 
    
    current_word, current_color = get_new_stimulus()
    last_match_state = is_match(current_word, current_color)
    
    word_label.config(text=current_word, fg=current_color)
    score_label.config(text=f"Điểm: {score} | Lượt: {current_round}/{MAX_ROUNDS} | Hãy phản ứng!")
    
    timer_id = root.after(INTERVAL_MS, update_word)

def handle_keypress(event):
    """Xử lý sự kiện nhấn phím Space."""
    global score, game_running, timer_id, input_received

    if not game_running or event.keysym != 'space' or input_received: return
    input_received = True 

    if timer_id: root.after_cancel(timer_id)
    
    if is_match(current_word, current_color):
        # ĐÚNG: Match và người chơi nhấn Space (+1 điểm)
        SOUND_CORRECT_PLAY()
        update_score(1, "✔️ Chính xác! +1 Điểm.")
        word_label.config(fg="lime green") 
        
    else:
        # SAI: Không Match nhưng người chơi nhấn Space (-1 điểm)
        SOUND_INCORRECT_PLAY()
        word_label.config(fg="red") 
        
        is_game_over = update_score(-1, f"❌ Sai! -1 Điểm.")
        
        # SỬA LỖI: Chỉ Game Over nếu điểm <= -3
        if is_game_over: 
            return # Trò chơi đã dừng trong update_score()

        # Nếu điểm số vẫn > -3, thông báo lỗi và tiếp tục lượt mới
        messagebox.showinfo("Lỗi", f"❌ Sai! -1 Điểm. Tiếp tục chơi...\nĐiểm hiện tại: {score}")

    # Chuyển sang lượt mới ngay sau khi xử lý input
    if game_running: 
        root.after(200, update_word) 


def start_game(event=None):
    """Bắt đầu trò chơi."""
    global game_running, score, current_round

    if game_running: return
    
    # Reset Max Attention
    
    game_running = True
    score = 0
    current_round = 0

    score_label.config(text=f"Điểm: 0 | Lượt: 0/{MAX_ROUNDS} | Nhấn Space khi MÀU CHỮ = NGHĨA")
    current_word, current_color = get_new_stimulus()
    word_label.config(text=current_word, fg=current_color)
    
    global timer_id
    if timer_id: root.after_cancel(timer_id)
    timer_id = root.after(INTERVAL_MS, update_word)


def stop_game(is_finished=False, reason=""):
    """Dừng trò chơi và hiển thị Max Attention."""
    global game_running, timer_id
    game_running = False
    
    if timer_id: root.after_cancel(timer_id)
    
    word_label.config(text="KẾT THÚC", fg="white")
    

    if is_finished:
        messagebox.showinfo("Hoàn thành!", f"Bạn đã hoàn thành {MAX_ROUNDS} lượt chơi.\nĐiểm số cuối cùng: {score}\n\n")
    elif reason == "SCORE_LIMIT":
        # Thông báo Game Over khi điểm <= -3
        messagebox.showinfo("Game Over", f"Thua cuộc! Điểm số đã xuống dưới {SCORE_LIMIT + 1}.\nĐiểm số cuối cùng: {score}\n\n")
    
    score_label.config(text=f"Điểm: {score} | Nhấn Enter để Bắt đầu")

def close_game(event):
    """Đóng cửa sổ."""
    root.destroy()

# --- GÁN SỰ KIỆN PHÍM TẮT ---
root.bind('<space>', handle_keypress) 
root.bind('<Return>', start_game)    
root.bind('<Escape>', close_game)    

# Khởi tạo màn hình chờ
word_label.config(text="Nhấn ENTER để bắt đầu", font=("Arial", 60, "bold"))

# Chạy giao diện
root.mainloop()