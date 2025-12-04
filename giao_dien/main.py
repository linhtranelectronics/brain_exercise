import tkinter as tk
from tkinter import ttk, messagebox
import os
import serial.tools.list_ports as list_ports
from PIL import Image, ImageTk
import serial
import sys
import time
import datetime
import csv
import threading # Giữ lại thư viện threading
from game1 import start_game_1
from game2 import start_game_2
from game3 import start_game_3  


# --- HẰNG SỐ CẤU HÌNH ---
WINDOW_WIDTH = 670
WINDOW_HEIGHT = 474
BAUD_RATE = 115200
UPDATE_INTERVAL_MS = 500 
GAME_COUNT = 4

# --- BIẾN TOÀN CỤC VÀ TRẠNG THÁI ---
root = tk.Tk()

# Trạng thái kết nối và Luồng
is_connected = False
serial_port_object = None 
selected_com_port = "" 

# Biến cờ để kiểm soát luồng đọc serial
is_reading_serial = False 
serial_thread = None

# Biến lưu trữ dữ liệu đọc được
serial_data = {
    'poor': 0,
    'attention': 0,
    'meditation': 0,
    'blink': 0
}

# Biến Tkinter để hiển thị điểm số
attention_var = tk.StringVar(value="0%")
meditation_var = tk.StringVar(value="0%")

# Danh sách các nút Game
game_buttons = []

# --- CHỨC NĂNG GHI LOG CSV ---
is_recording = False
csv_file = None
csv_writer = None

def get_timestamp_filename():
    """Tạo tên file theo định dạng Month_date_hour_minute_second.csv"""
    now = datetime.datetime.now()
    return now.strftime("%m_%d_%H_%M_%S") + ".csv"

def toggle_recording():
    """Bắt đầu hoặc Dừng ghi dữ liệu vào file CSV."""
    global is_recording, csv_file, csv_writer
    
    if not is_connected:
        messagebox.showwarning("Cảnh báo", "Vui lòng kết nối cổng COM trước khi ghi dữ liệu.")
        return

    if not is_recording:
        # BẮT ĐẦU GHI
        try:
            filename = get_timestamp_filename()
            csv_file = open(filename, 'w', newline='')
            csv_writer = csv.writer(csv_file)
            
            # Ghi hàng tiêu đề
            csv_writer.writerow(['Timestamp', 'PoorQuality', 'Attention', 'Meditation', 'Blink'])
            
            is_recording = True
            record_button.config(text="Dừng Ghi (CSV)", style='Disconnect.TButton')
            messagebox.showinfo("Thông báo", f"Bắt đầu ghi dữ liệu vào: {filename}")
        
        except Exception as e:
            messagebox.showerror("Lỗi ghi file", f"Không thể mở file CSV: {e}")
            is_recording = False 
    else:
        # DỪNG GHI
        if csv_file:
            csv_file.close()
            csv_file = None
        is_recording = False
        record_button.config(text="Ghi Dữ Liệu (CSV)", style='Connect.TButton')
        messagebox.showinfo("Thông báo", "Đã dừng ghi dữ liệu CSV.")

def write_data_to_csv():
    """Ghi dữ liệu hiện tại vào file CSV nếu đang ở trạng thái ghi."""
    global is_recording, csv_writer
    
    if is_recording and csv_writer:
        try:
            current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            row = [
                current_time,
                serial_data['poor'],
                serial_data['attention'],
                serial_data['meditation'],
                serial_data['blink']
            ]
            csv_writer.writerow(row)
        except Exception as e:
            print(f"Lỗi khi ghi vào file CSV: {e}")
            toggle_recording() 

# --- CẤU HÌNH CỬA SỔ CHÍNH ---
def setup_main_window():
    root.title("Hệ thống Thể dục cho Não bộ")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)

setup_main_window()

# --- HÀM HỖ TRỢ VÀ LOGIC SERIAL (TRONG THREAD RIÊNG) ---

def get_available_com_ports():
    """Quét và trả về danh sách các cổng COM có sẵn."""
    try:
        ports = [port.device for port in list_ports.comports()]
        return ["Chọn cổng..."] + ports
    except Exception as e:
        print(f"Lỗi khi quét cổng COM: {e}")
        return ["Chọn cổng..."]

def serial_reader_thread():
    """Hàm đọc dữ liệu serial chạy trên luồng nền."""
    global serial_port_object
    global serial_data
    global is_reading_serial

    while is_reading_serial:
        if serial_port_object is None or not serial_port_object.is_open:
            time.sleep(0.1)
            continue
            
        try:
            if serial_port_object.in_waiting > 0:
                line = serial_port_object.readline().decode('utf-8').strip()

                if line:
                    try:
                        values = line.split(',')
                        if len(values) == 4:
                            # Cập nhật dữ liệu vào biến toàn cục
                            data = [int(v) for v in values]
                            serial_data['poor'] = data[0]
                            serial_data['attention'] = data[1]
                            serial_data['meditation'] = data[2]
                            serial_data['blink'] = data[3]
                            # print(f"Đọc Serial: {serial_data}") # Debug
                    except ValueError:
                        print(f"Lỗi chuyển đổi giá trị: {line}")
            else:
                # Đợi một chút nếu không có dữ liệu để tránh chiếm CPU quá mức
                time.sleep(0.01)

        except serial.SerialException as e:
            print(f"Lỗi kết nối Serial trong thread: {e}")
            # Dùng root.after để gọi hàm ngắt kết nối trên luồng chính
            root.after(0, connect_disconnect) 
            is_reading_serial = False
        except Exception as e:
            print(f"Lỗi không xác định trong thread: {e}")
            is_reading_serial = False

            
def update_gui_data():
    """Cập nhật GUI và ghi CSV (Chạy trên luồng chính)."""
    
    if is_connected:
        # Chỉ cập nhật GUI dựa trên dữ liệu đã đọc được ở luồng nền
        attention_var.set(f"{serial_data['attention']}%")
        meditation_var.set(f"{serial_data['meditation']}%")
        
        # GHI DỮ LIỆU VÀO CSV
        write_data_to_csv()

    # Lên lịch gọi lại hàm này sau khoảng thời gian UPDATE_INTERVAL_MS
    root.after(UPDATE_INTERVAL_MS, update_gui_data)

# --- LOGIC GIAO DIỆN (GUI) ---

def toggle_game_buttons(is_visible):
    """Ẩn hoặc hiện các nút Game."""
    button_width = 120
    button_height = 80
    start_x = 30
    spacing_x = 43

    if is_visible:
        for index, btn in enumerate(game_buttons):
            pos_x = start_x + (button_width + spacing_x) * index
            btn.place(x=pos_x, y=350, width=button_width, height=button_height)
    else:
        for btn in game_buttons:
            btn.place_forget()

def connect_disconnect():
    """Hàm xử lý Kết nối và Ngắt kết nối cổng Serial."""
    global is_connected, serial_port_object, selected_com_port
    global is_reading_serial, serial_thread

    selected_com_port = com_combobox.get()
    
    if not is_connected:
        # LOGIC KẾT NỐI
        valid_ports = get_available_com_ports()
        if selected_com_port not in valid_ports or selected_com_port == "Chọn cổng...":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một cổng COM hợp lệ.")
            return

        try:
            serial_port_object = serial.Serial(selected_com_port, baudrate=BAUD_RATE, timeout=0.1) # Giảm timeout
            
            # BẮT ĐẦU LUỒNG ĐỌC SERIAL
            is_reading_serial = True
            serial_thread = threading.Thread(target=serial_reader_thread, daemon=True) # daemon=True để luồng tự đóng khi ứng dụng thoát
            serial_thread.start()
            
            # Cập nhật trạng thái GUI
            is_connected = True
            connect_button.config(text="Ngắt kết nối", style='Disconnect.TButton')
            com_combobox.config(state='disabled')
            
            toggle_game_buttons(True) 
            record_button.place(x=WINDOW_WIDTH - 200, y=WINDOW_HEIGHT - 35, width=100)
            
            messagebox.showinfo("Kết nối", f"Đã kết nối tới cổng: {selected_com_port}")

        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối tới {selected_com_port}: {e}")
            is_connected = False
            
    else:
        # LOGIC NGẮT KẾT NỐI
        
        # Dừng ghi dữ liệu nếu đang ghi
        if is_recording:
            toggle_recording()
            
        # DỪNG LUỒNG ĐỌC SERIAL
        is_reading_serial = False
        if serial_thread and serial_thread.is_alive():
            serial_thread.join(timeout=0.2) # Chờ luồng kết thúc (tối đa 0.2s)
            
        if serial_port_object and serial_port_object.is_open:
             serial_port_object.close()
             print(f"close Serial {selected_com_port}.")
        
        # Cập nhật trạng thái GUI
        is_connected = False
        connect_button.config(text="Kết nối", style='Connect.TButton')
        com_combobox.config(state='readonly')
        
        toggle_game_buttons(False)
        record_button.place_forget() 
        
        attention_var.set("0%")
        meditation_var.set("0%")
        
        messagebox.showinfo("Thông báo", f"Đã ngắt kết nối khỏi cổng: {selected_com_port}")


def run_game(game_number):
    """Hàm xử lý sự kiện khi nhấn nút Game."""
    if is_connected:
        # Dừng ghi dữ liệu và luồng serial trước khi vào game
        if is_recording:
            toggle_recording()
        
        # DỪNG LUỒNG SERIAL (nếu cần thiết, tùy thuộc vào game)
        # Trong trường hợp này, ta giả định game tự quản lý serial
        
        if game_number == 1:
            # Lưu ý: Nếu game1.py cũng sử dụng cổng serial, bạn cần truyền đối tượng
            # serial đã đóng hoặc quản lý việc mở lại cổng cẩn thận.
            start_game_1()  # Gọi hàm chơi game 1 từ game1.py
        elif game_number == 2:
            start_game_2()  # Gọi hàm chơi game 2 từ game2.py
        elif game_number == 3:
            start_game_3()  # Gọi hàm chơi game 3 từ game3.py
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng kết nối cổng COM trước khi chơi Game.")

def exit_app():
    """Hàm thoát ứng dụng. Đóng kết nối serial và file CSV trước khi thoát."""
    global serial_port_object
    global is_reading_serial, serial_thread
    
    if is_reading_serial:
        is_reading_serial = False
        if serial_thread and serial_thread.is_alive():
            serial_thread.join(timeout=0.2) 
            
    if is_recording:
        toggle_recording() 
    if is_connected:
        if serial_port_object and serial_port_object.is_open:
             serial_port_object.close()
    root.quit()

# --- THIẾT LẬP STYLE VÀ LAYOUT (GIỮ NGUYÊN) ---

style = ttk.Style()
style.configure('Game.TButton', font=('Arial', 16, 'bold'), padding=(15, 15))
style.configure('Connect.TButton', font=('Arial', 12, 'bold'), foreground='black', background='#008CBA', borderwidth=1)
style.map('Connect.TButton', background=[('active', '#007B9E')])
style.configure('Disconnect.TButton', font=('Arial', 12, 'bold'), foreground='black', background='#f44336', borderwidth=1)
style.map('Disconnect.TButton', background=[('active', '#D32F2F')])

# Khung chứa Logo và Tiêu đề
try:
    img_pil = Image.open(r"E:\arduino\mindway_mobile\giao_dien\img\banner.png")
    img_pil = img_pil.resize((656, 84), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_pil)
    image_label = tk.Label(root, image=img_tk)
    image_label.pack(pady=10)
    image_label.image = img_tk 
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file 'banner.png'. Đảm bảo đường dẫn chính xác.")
    tk.Label(root, text="Hệ thống Thể dục cho Não bộ", font=("Arial", 18, "bold")).pack(pady=10)


# Khung nội dung chính (Phần giữa)
main_content_frame = tk.Frame(root, bg="white")
main_content_frame.pack(fill='both', expand=True, padx=20, pady=10)

# Khung trái: Thông tin dự án và COM
left_frame = tk.Frame(main_content_frame, bg="white")
left_frame.pack(side='left', fill='y', padx=10, pady=10)

tk.Label(left_frame, text="Đề tài: Hệ thống Thể dục cho Não bộ", font=("Arial", 14), bg="white").pack(anchor='w', pady=(10, 5))
tk.Label(left_frame, text="Học sinh: Đức Dũng - Thiên Phúc", font=("Arial", 14), bg="white").pack(anchor='w')
tk.Label(left_frame, text="GVHD: Tống Ngọc Trâm Anh", font=("Arial", 14), bg="white").pack(anchor='w', pady=(0, 30))

tk.Label(left_frame, text="Chọn cổng COM", font=("Arial", 12), bg="white").pack(anchor='w')

com_ports = get_available_com_ports()
com_combobox = ttk.Combobox(
    left_frame, 
    values=com_ports, 
    state='readonly', 
    width=15, 
    font=("Arial", 12)
)
com_combobox.set(com_ports[0]) 
com_combobox.place(x=130, y=130)

connect_button = ttk.Button(
    left_frame, 
    text="Kết nối", 
    command=connect_disconnect, 
    style='Connect.TButton' 
)
connect_button.place(x=100, y =160)

# Khung phải: Trạng thái (Attention/Meditation)
right_frame = tk.Frame(main_content_frame, bg="white")
right_frame.pack(side='right', fill='y', padx=10, pady=10)

tk.Label(right_frame, text="Attention (Tập trung):", font=("Arial", 14), bg="white").pack(anchor='w', pady=(10, 5))
ttk.Label(right_frame, textvariable=attention_var, font=("Arial", 18, "bold"), foreground="blue").pack(anchor='w', padx=20)

tk.Label(right_frame, text="Meditation (Thư giãn):", font=("Arial", 14), bg="white").pack(anchor='w', pady=(20, 5))
ttk.Label(right_frame, textvariable=meditation_var, font=("Arial", 18, "bold"), foreground="green").pack(anchor='w', padx=20)


# Tạo các nút Game và lưu vào list game_buttons
for i in range(1, GAME_COUNT + 1):
    btn = ttk.Button(
        root, 
        text=f"Game {i}", 
        command=lambda i=i: run_game(i), 
        width=5, 
        style='Game.TButton'
    )
    game_buttons.append(btn)
    
# TẠO NÚT GHI DỮ LIỆU VÀ ĐẶT VỊ TRÍ
record_button = ttk.Button(
    root, 
    text="Ghi Dữ Liệu (CSV)", 
    command=toggle_recording, 
    style='Connect.TButton'
)

# Nút Exit (Thoát)
exit_button = ttk.Button(
    root, 
    text="Exit", 
    command=exit_app, 
    width=5
)
exit_button.place(x=WINDOW_WIDTH - 90, y=WINDOW_HEIGHT - 35, width=80) 


# --- VÒNG LẶP CHÍNH CỦA ỨNG DỤNG ---
if __name__ == "__main__":
    update_gui_data() 
    root.mainloop()