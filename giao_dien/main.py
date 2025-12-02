# import tkinter as tk
# from tkinter import ttk, messagebox
# import os
# import serial.tools.list_ports as list_ports # Dùng để mô phỏng quét cổng COM
# from PIL import Image, ImageTk
# #import ReadSerial
# import time
# import sys
# import serial

# # --- Cấu hình cửa sổ chính ---
# window_width = 670
# window_height = 474
# root = tk.Tk()
# root.title("Hệ thống thể dục cho não bộ")
# root.geometry(f"{window_width}x{window_height}")
# root.resizable(False, False) # Không cho phép thay đổi kích thước

# # Biến toàn cục để theo dõi trạng thái kết nối
# is_connected = False
# # Biến chứa các đối tượng nút Game
# game_buttons = []

# # --- Hàm hỗ trợ ---

# PARAM_NAMES = ['poor', 'attention', 'meditation', 'blink']
# BAUD_RATE = 115200

# def read_serial_data():
    
#     global SERIAL_PORT
#     global poor, attention, meditation, blink
#     root.after(500)  
#     if ser is None or not ser.is_open:
#         # Dừng vòng lặp .after() nếu cổng bị đóng
#         return
    
#     try:
#         # Read a line of data (terminated by '\n' sent by Serial.println())
#         if ser.in_waiting > 0:
#             # Read bytes, decode to string, and remove newline characters ('\r\n')
#             line = ser.readline().decode('utf-8').strip()

#             if line:
#                 try:
#                     # Split the string by comma
#                     values = line.split(',')

#                     # Ensure there are exactly 4 values
#                     if len(values) == 4:
#                         # Convert string values to integers
#                         data = [int(v) for v in values]

#                         # Print to screen in a clear format
#                         #print(f"Poor: {data[0]:<3} | Attention: {data[1]:<3} | Meditation: {data[2]:<3} | Blink: {data[3]}")
#                         poor = data[0]
#                         attention = data[1]
#                         meditation = data[2]
#                         blink = data[3]
#                         attention_var.set(str(attention) + "%")
#                         meditation_var.set(str(meditation) + "%")
#                     # else:
#                     #     print(f"Data error: {line} (Expected 4 values)")

#                 except ValueError:
#                     # Catch error if values are not integers
#                     print(f"Value conversion error: {line}")
                

#     except serial.SerialException as e:
#         print(f"Serial connection error: {e}")
#         print(f"Please check port '{selected_com}' and ensure Arduino is connected and the port is free.")
#     except KeyboardInterrupt:
#         print("\nPython program stopped.")
#     finally:
#         if 'ser' in locals() and ser.is_open:
#             ser.close()
#             print("Serial port closed.")

# def get_available_com_ports():
#     """Mô phỏng quét các cổng COM có sẵn."""
#     # Trong môi trường thực tế, bạn sẽ dùng thư viện pyserial:
#     ports = [port.device for port in list_ports.comports()]
#     return ports
    
#     # Hiện tại, chỉ trả về các giá trị mô phỏng
#     #return ["Chọn cổng...", "COM3", "COM4", "COM10"]

# def toggle_game_buttons(state):
#     """
#     Ẩn (state=False) hoặc hiện (state=True) các nút Game.
#     Sử dụng place() để quản lý vị trí thay vì pack()
#     """
#     if state:
#         for btn in game_buttons:
#             #btn.pack(side='left', padx=(5, 10), pady=20, expand=True)
#             btn.place(x=40 + (btn.winfo_reqwidth() + 40) * game_buttons.index(btn), y=350, width=150, height=80  )
#     else:
#         for btn in game_buttons:
#             btn.place_forget()

# # --- Hàm xử lý sự kiện chính ---

# def connect_disconnect():
#     """Hàm xử lý Kết nối và Ngắt kết nối."""
#     global is_connected
#     global ser
#     global selected_com 
#     selected_com = com_combobox.get()
    
#     if not is_connected:
#         # LOGIC KẾT NỐI
#         if selected_com in get_available_com_ports() and selected_com != "Chọn cổng...":
            
#             # --- Mô phỏng quá trình kết nối ---
#             try:
#                 # Tại đây sẽ thực hiện kết nối serial (ví dụ: ser = serial.Serial(selected_com, baudrate=9600))
#                 # Giả định kết nối thành công:
#                 ser = serial.Serial(selected_com, baudrate=115200, timeout=1)
#                 is_connected = True
#                 connect_button.config(text="Ngắt kết nối", style='Disconnect.TButton')
#                 com_combobox.config(state='disabled') # Khóa Combobox khi đã kết nối
                
#                 # Hiển thị các nút Game
#                 toggle_game_buttons(True) 
                
#                 #messagebox.showinfo("Kết nối thành công", f"Đã kết nối tới cổng: {selected_com}")
                
#             except Exception as e:
#                 #messagebox.showerror("Lỗi kết nối", f"Không thể kết nối tới {selected_com}: {e}")
#                 is_connected = False
#         else:
#             messagebox.showwarning("Cảnh báo", "Vui lòng chọn một cổng COM hợp lệ.")
            
#     else:
#         # LOGIC NGẮT KẾT NỐI
        
#         # --- Mô phỏng quá trình ngắt kết nối ---
#         # Tại đây sẽ thực hiện ngắt kết nối serial (ví dụ: ser.close())
        
#         is_connected = False
#         ser.close()
#         connect_button.config(text="Kết nối", style='Connect.TButton')
#         com_combobox.config(state='readonly') # Mở khóa Combobox
        
#         # Ẩn các nút Game
#         toggle_game_buttons(False)
        
#         # Reset điểm số
#         attention_var.set("0%")
#         meditation_var.set("0%")
        
#         #messagebox.showinfo("Thông báo", f"Đã ngắt kết nối khỏi cổng: {selected_com}")


# def run_game(game_number):
#     """Hàm xử lý sự kiện khi nhấn nút Game."""
#     if is_connected:
#         if game_number == 1:
#             import game1
#     else:
#         messagebox.showwarning("Cảnh báo", "Vui lòng kết nối cổng COM trước khi chơi Game.")

# def exit_app():
#     """Hàm thoát ứng dụng."""
#     if is_connected:
#         connect_disconnect() # Ngắt kết nối trước khi thoát (Nếu cần)
#     root.quit()

# # --- Thiết lập Style (Cho nút Kết nối/Ngắt kết nối) ---
# style = ttk.Style()
# # Style cho nút Game

# style.configure('Game.TButton', font=('Arial', 16, 'bold'), padding=(20, 20))

# # Style cho trạng thái Kết nối (Màu xanh)
# style.configure('Connect.TButton', font=('Arial', 12, 'bold'), foreground='black', background='#008CBA', borderwidth=1)
# # Style cho trạng thái Ngắt kết nối (Màu đỏ)
# style.configure('Disconnect.TButton', font=('Arial', 12, 'bold'), foreground='black', background='#f44336', borderwidth=1)
# style.map('Connect.TButton', background=[('active', '#007B9E')])
# style.map('Disconnect.TButton', background=[('active', '#D32F2F')])

# # --- Khung chứa Logo và Tiêu đề (Phần trên cùng) ---

# img_pil = Image.open(r"E:\arduino\mindway_mobile\giao_dien\img\banner.png") 
# img_pil = img_pil.resize((656, 84), Image.LANCZOS)
# img_tk = ImageTk.PhotoImage(img_pil)
# image_label = tk.Label(root, image=img_tk)
# image_label.pack(pady=10)


# image_label.image = img_tk


# # # --- Khung nội dung chính (Phần giữa) ---
# main_content_frame = tk.Frame(root, bg="white")
# main_content_frame.pack(fill='both', expand=True, padx=20, pady=10)

# # # --- Khung trái: Thông tin dự án và COM ---
# left_frame = tk.Frame(main_content_frame, bg="white")
# left_frame.pack(side='left', fill='y', padx=10, pady=10)

# tk.Label(left_frame, text="Đề tài: Hệ thống thể dục cho não bộ", font=("Arial", 14), bg="white").pack(anchor='w', pady=(10, 5))
# tk.Label(left_frame, text="HS:", font=("Arial", 14), bg="white").pack(anchor='w')
# tk.Label(left_frame, text="GVHD:", font=("Arial", 14), bg="white").pack(anchor='w', pady=(0, 30))

# # Chọn cổng COM (Sử dụng Combobox)
# tk.Label(left_frame, text="Chọn cổng COM", font=("Arial", 12), bg="white").pack(anchor='w')

# com_ports = get_available_com_ports()
# com_combobox = ttk.Combobox(
#     left_frame, 
#     values=com_ports, 
#     state='readonly', # Chỉ cho phép chọn từ danh sách
#     width=15, 
#     font=("Arial", 12)
# )
# com_combobox.set(com_ports[0]) # Đặt giá trị mặc định là "Chọn cổng..."
# com_combobox.place(x=130, y=130)

# # Nút Kết nối/Ngắt kết nối
# connect_button = ttk.Button(
#     left_frame, 
#     text="Kết nối", 
#     command=connect_disconnect, 
#     style='Connect.TButton' # Dùng style Kết nối mặc định
# )
# connect_button.place(x=100, y =160)


# # --- Khung phải: Trạng thái (Attention/Meditation) ---
# right_frame = tk.Frame(main_content_frame, bg="white")
# right_frame.pack(side='right', fill='y', padx=10, pady=10)

# attention_var = tk.StringVar(value="0%")
# meditation_var = tk.StringVar(value="0%")

# tk.Label(right_frame, text="attention:", font=("Arial", 14), bg="white").pack(anchor='w', pady=(10, 5))
# ttk.Label(right_frame, textvariable=attention_var, font=("Arial", 14, "bold"), foreground="blue").pack(anchor='w', padx=20)

# tk.Label(right_frame, text="meditation:", font=("Arial", 14), bg="white").pack(anchor='w', pady=(20, 5))
# ttk.Label(right_frame, textvariable=meditation_var, font=("Arial", 14, "bold"), foreground="green").pack(anchor='w', padx=20)


# # --- Khung nút Game (Phần dưới cùng) ---
# # game_button_frame = tk.Frame(root, bg="black", height=150)
# # game_button_frame.pack(fill='x', side='bottom', padx=50, pady=(0, 10))
# # game_button_frame.pack_propagate(False)

# # Tạo 4 nút Game và lưu vào list game_buttons
# for i in range(1, 5):
#     btn = ttk.Button( root, text=f"Game {i}", command=lambda i=i: run_game(i), width=5, style='Game.TButton' )
#     game_buttons.append(btn)

    
# # Quan trọng: Các nút Game chưa được pack() hay place() vào giao diện ban đầu


# # Nút Exit (Thoát)
# exit_button = ttk.Button(root, text="Exit", command=exit_app, width=5)
# exit_button.place(x=window_width - 60, y=window_height - 35)


# # --- Vòng lặp chính của ứng dụng ---

# def update_serial_data():
#     """Hàm cập nhật dữ liệu serial định kỳ."""
#     if is_connected:
#         read_serial_data()
#         # Cập nhật điểm số
#         attention_var.set(str(attention) + "%")
#         meditation_var.set(str(meditation) + "%")
#     root.after(500, update_serial_data)  # Lên lịch gọi lại sau 500ms

# update_serial_data()  # Bắt đầu vòng lặp cập nhật dữ liệu serial
# root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
import os
import serial.tools.list_ports as list_ports
from PIL import Image, ImageTk
import serial
import sys
import time
import threading 

# --- HẰNG SỐ CẤU HÌNH ---
WINDOW_WIDTH = 670
WINDOW_HEIGHT = 474
BAUD_RATE = 115200
UPDATE_INTERVAL_MS = 500  # Khoảng thời gian cập nhật dữ liệu serial (ms)
GAME_COUNT = 4

# --- BIẾN TOÀN CỤC VÀ TRẠNG THÁI ---
# Đối tượng cửa sổ chính
root = tk.Tk()

# Trạng thái kết nối
is_connected = False
serial_port_object = None  # Đối tượng SerialPort của PySerial
selected_com_port = ""     # Cổng COM đã chọn

# Biến Tkinter để hiển thị điểm số
attention_var = tk.StringVar(value="0%")
meditation_var = tk.StringVar(value="0%")

# Biến lưu trữ dữ liệu đọc được từ cổng serial
serial_data = {
    'poor': 0,
    'attention': 0,
    'meditation': 0,
    'blink': 0
}

# Danh sách các nút Game
game_buttons = []

# --- CẤU HÌNH CỬA SỔ CHÍNH ---
def setup_main_window():
    """Thiết lập các thuộc tính cơ bản cho cửa sổ chính."""
    root.title("Hệ thống Thể dục cho Não bộ")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False) # Không cho phép thay đổi kích thước

setup_main_window()

# --- HÀM HỖ TRỢ VÀ LOGIC SERIAL ---

def get_available_com_ports():
    """Quét và trả về danh sách các cổng COM có sẵn."""
    try:
        # Sử dụng thư viện pyserial để quét cổng thực tế
        ports = [port.device for port in list_ports.comports()]
        return ["Chọn cổng..."] + ports
        #return  ports
    except Exception as e:
        print(f"Lỗi khi quét cổng COM: {e}")
        return ["Chọn cổng..."]

def read_serial_data():
    """
    Đọc dữ liệu từ cổng serial và cập nhật biến `serial_data`.
    Dữ liệu được mong đợi ở định dạng 'poor,attention,meditation,blink'.
    """
    global serial_port_object
    global serial_data

    # Kiểm tra xem cổng serial có đang mở hay không
    if serial_port_object is None or not serial_port_object.is_open:
        return

    try:
        # Đọc dữ liệu nếu có sẵn
        if serial_port_object.in_waiting > 0:
            # Đọc một dòng, giải mã sang UTF-8, và loại bỏ ký tự ngắt dòng
            line = serial_port_object.readline().decode('utf-8').strip()

            if line:
                try:
                    # Tách chuỗi theo dấu phẩy
                    values = line.split(',')

                    # Đảm bảo có đúng 4 giá trị
                    if len(values) == 4:
                        # Chuyển đổi giá trị string sang integer
                        data = [int(v) for v in values]

                        # Cập nhật biến global/dict
                        serial_data['poor'] = data[0]
                        serial_data['attention'] = data[1]
                        serial_data['meditation'] = data[2]
                        serial_data['blink'] = data[3]
                        
                        # Cập nhật hiển thị lên GUI (sẽ được gọi trong update_gui_data)
                        
                    # else:
                    #     print(f"Lỗi định dạng dữ liệu: {line} (Dữ liệu mong đợi 4 giá trị)")

                except ValueError:
                    # Bắt lỗi nếu các giá trị không phải là số nguyên
                    print(f"Lỗi chuyển đổi giá trị: {line}")

    except serial.SerialException as e:
        # Bắt các lỗi liên quan đến kết nối serial
        print(f"Lỗi kết nối Serial: {e}")
        messagebox.showerror("Lỗi Serial", f"Mất kết nối tới {selected_com_port}: {e}")
        # Tự động ngắt kết nối GUI nếu xảy ra lỗi nghiêm trọng
        connect_disconnect() 
    except KeyboardInterrupt:
        print("\nChương trình Python bị dừng.")
        if serial_port_object and serial_port_object.is_open:
            serial_port_object.close()
            
def update_gui_data():
    """
    Hàm cập nhật dữ liệu serial định kỳ và lên lịch gọi lại chính nó.
    Đây là cơ chế chính để đọc dữ liệu trong vòng lặp Tkinter.
    """
    if is_connected:
        read_serial_data()
        # Cập nhật biến Tkinter để hiển thị trên giao diện
        attention_var.set(f"{serial_data['attention']}%")
        meditation_var.set(f"{serial_data['meditation']}%")
        
    # Lên lịch gọi lại hàm này sau khoảng thời gian UPDATE_INTERVAL_MS
    root.after(UPDATE_INTERVAL_MS, update_gui_data)

# --- LOGIC GIAO DIỆN (GUI) ---

def toggle_game_buttons(is_visible):
    """
    Ẩn (is_visible=False) hoặc hiện (is_visible=True) các nút Game.
    Sử dụng place() để quản lý vị trí.
    """
    button_width = 120
    button_height = 80
    start_x = 30
    spacing_x = 43

    if is_visible:
        for index, btn in enumerate(game_buttons):
            # Tính toán vị trí X dựa trên index của nút
            pos_x = start_x + (button_width + spacing_x) * index
            btn.place(x=pos_x, y=350, width=button_width, height=button_height)
    else:
        for btn in game_buttons:
            btn.place_forget() # Ẩn nút

def connect_disconnect():
    """Hàm xử lý Kết nối và Ngắt kết nối cổng Serial."""
    global is_connected
    global serial_port_object
    global selected_com_port

    selected_com_port = com_combobox.get()
    
    if not is_connected:
        # LOGIC KẾT NỐI
        
        # Kiểm tra xem cổng đã chọn có hợp lệ không
        valid_ports = get_available_com_ports()
        if selected_com_port not in valid_ports or selected_com_port == "Chọn cổng...":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một cổng COM hợp lệ.")
            return

        # Thực hiện kết nối serial
        try:
            # Mở cổng serial với Baud Rate đã cấu hình
            serial_port_object = serial.Serial(selected_com_port, baudrate=BAUD_RATE, timeout=1)
            
            # Cập nhật trạng thái GUI và biến trạng thái
            is_connected = True
            connect_button.config(text="Ngắt kết nối", style='Disconnect.TButton')
            com_combobox.config(state='disabled') # Khóa Combobox khi đã kết nối
            
            # Hiển thị các nút Game
            toggle_game_buttons(True) 
            messagebox.showinfo("Kết nối", f"Đã kết nối tới cổng: {selected_com_port}")

        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối tới {selected_com_port}: {e}")
            is_connected = False
            
    else:
        # LOGIC NGẮT KẾT NỐI
        if serial_port_object and serial_port_object.is_open:
             serial_port_object.close()
             print(f"Đã đóng cổng serial {selected_com_port}.")
        
        # Cập nhật trạng thái GUI và biến trạng thái
        is_connected = False
        connect_button.config(text="Kết nối", style='Connect.TButton')
        com_combobox.config(state='readonly') # Mở khóa Combobox
        
        # Ẩn các nút Game
        toggle_game_buttons(False)
        
        # Reset điểm số hiển thị
        attention_var.set("0%")
        meditation_var.set("0%")
        
        messagebox.showinfo("Thông báo", f"Đã ngắt kết nối khỏi cổng: {selected_com_port}")


def run_game(game_number):
    """Hàm xử lý sự kiện khi nhấn nút Game. Tải và chạy script game tương ứng."""
    if is_connected:
        if game_number == 1:
            import game1
        elif game_number == 2:
            import game2   
        elif game_number == 3:
            import game3   
        elif game_number == 4:
            import game4
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng kết nối cổng COM trước khi chơi Game.")

def exit_app():
    """Hàm thoát ứng dụng. Đóng kết nối serial trước khi thoát."""
    global serial_port_object
    if is_connected:
        # Ngắt kết nối trước khi thoát
        if serial_port_object and serial_port_object.is_open:
             serial_port_object.close()
    root.quit()

# --- THIẾT LẬP STYLE ---
style = ttk.Style()
# Style cho nút Game
style.configure('Game.TButton', font=('Arial', 16, 'bold'), padding=(15, 15))

# Style cho trạng thái Kết nối (Màu xanh)
style.configure('Connect.TButton', font=('Arial', 12, 'bold'), foreground='black', background='#008CBA', borderwidth=1)
style.map('Connect.TButton', background=[('active', '#007B9E')])

# Style cho trạng thái Ngắt kết nối (Màu đỏ)
style.configure('Disconnect.TButton', font=('Arial', 12, 'bold'), foreground='black', background='#f44336', borderwidth=1)
style.map('Disconnect.TButton', background=[('active', '#D32F2F')])

# --- CẤU TRÚC GIAO DIỆN (LAYOUT) ---

# Khung chứa Logo và Tiêu đề (Phần trên cùng)
try:
    # Thay đổi đường dẫn ảnh nếu cần
    img_pil = Image.open(r"E:\arduino\mindway_mobile\giao_dien\img\banner.png")
    img_pil = img_pil.resize((656, 84), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_pil)
    image_label = tk.Label(root, image=img_tk)
    image_label.pack(pady=10)
    image_label.image = img_tk # Giữ tham chiếu để ảnh không bị Garbage Collected
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file 'banner.png'. Đảm bảo đường dẫn chính xác.")
    # Tạo một Label trống thay thế nếu không tìm thấy ảnh
    tk.Label(root, text="Hệ thống Thể dục cho Não bộ", font=("Arial", 18, "bold")).pack(pady=10)


# Khung nội dung chính (Phần giữa)
main_content_frame = tk.Frame(root, bg="white")
main_content_frame.pack(fill='both', expand=True, padx=20, pady=10)

# Khung trái: Thông tin dự án và COM
left_frame = tk.Frame(main_content_frame, bg="white")
left_frame.pack(side='left', fill='y', padx=10, pady=10)

# Hiển thị thông tin dự án
tk.Label(left_frame, text="Đề tài: Hệ thống Thể dục cho Não bộ", font=("Arial", 14), bg="white").pack(anchor='w', pady=(10, 5))
tk.Label(left_frame, text="Học sinh: Đức Dũng - Thiên Phúc", font=("Arial", 14), bg="white").pack(anchor='w')
tk.Label(left_frame, text="GVHD: Tống Ngọc Trâm Anh", font=("Arial", 14), bg="white").pack(anchor='w', pady=(0, 30))

# Chọn cổng COM (Sử dụng Combobox)
tk.Label(left_frame, text="Chọn cổng COM", font=("Arial", 12), bg="white").pack(anchor='w')

com_ports = get_available_com_ports()
com_combobox = ttk.Combobox(
    left_frame, 
    values=com_ports, 
    state='readonly', # Chỉ cho phép chọn từ danh sách
    width=15, 
    font=("Arial", 12)
)
com_combobox.set(com_ports[0]) # Đặt giá trị mặc định (ví dụ: "Chọn cổng..." hoặc cổng đầu tiên)
com_combobox.place(x=130, y=130)

# Nút Kết nối/Ngắt kết nối
connect_button = ttk.Button(
    left_frame, 
    text="Kết nối", 
    command=connect_disconnect, 
    style='Connect.TButton' # Dùng style Kết nối mặc định
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
    
# Quan trọng: Các nút Game chưa được hiển thị (place_forget) cho đến khi kết nối thành công.


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
    # Bắt đầu vòng lặp cập nhật dữ liệu serial
    update_gui_data() 
    
    # Bắt đầu vòng lặp sự kiện của Tkinter
    root.mainloop()