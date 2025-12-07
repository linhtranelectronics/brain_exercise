import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- 1. Hàm Xử Lý Mở File và Vẽ Biểu Đồ ---
def draw_line_chart(frame):
    """Mở hộp thoại chọn file CSV, đọc dữ liệu và vẽ biểu đồ đường đa tuyến."""
    
    # Mở hộp thoại chọn file
    file_path = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if not file_path:
        return # Người dùng hủy chọn file

    try:
        # Đọc dữ liệu từ file CSV
        df = pd.read_csv(file_path)

        # Kiểm tra xem DataFrame có đủ cột để vẽ không
        # Cần ít nhất 1 cột X và 1 cột Y
        if df.shape[1] < 2:
            messagebox.showerror("Lỗi Dữ Liệu", "Tệp CSV phải có ít nhất 2 cột.")
            return

        # Xác định cột X (thường là cột đầu tiên)
        col_x = df.columns[0]
        
        # Xác định các cột Y (tất cả các cột còn lại)
        cols_y = df.columns[1:] 

        # --- 2. Xóa biểu đồ cũ (nếu có) ---
        for widget in frame.winfo_children():
            widget.destroy()

        # --- 3. Tạo Biểu Đồ Matplotlib ---
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # --- Lặp qua các cột Y và vẽ từng đường ---
        for col in cols_y:
            # Vẽ biểu đồ đường, Matplotlib sẽ tự động chọn màu khác nhau cho mỗi lần gọi
            ax.plot(df[col_x], df[col], marker='o', label=col) 
        
        # Thiết lập tiêu đề và nhãn trục
        ax.set_title(f"Biểu đồ Xu Hướng: {', '.join(cols_y)} theo {col_x}", fontsize=14)
        ax.set_xlabel(col_x, fontsize=12)
        ax.set_ylabel("Giá Trị / Tần Số", fontsize=12)
        ax.legend(title="Chú giải Dữ liệu") # Thêm chú giải
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # --- 4. Tích hợp Matplotlib vào Tkinter ---
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=1)
        canvas.draw()
        
    except Exception as e:
        messagebox.showerror("Lỗi Xử Lý", f"Đã xảy ra lỗi khi đọc hoặc vẽ biểu đồ: {e}")

# --- 5. Thiết lập Giao Diện Tkinter ---
root = tk.Tk()
root.title("Trực Quan Hóa Dữ Liệu CSV - Biểu Đồ Đường")
root.geometry("900x650")

# Khung chứa nút điều khiển
control_frame = tk.Frame(root, bg='#f0f0f0')
control_frame.pack(pady=10, fill=tk.X)

# Nút "Open File"
open_button = tk.Button(
    control_frame, 
    text="🗓️ Open File CSV và Vẽ Biểu Đồ", 
    command=lambda: draw_line_chart(chart_frame), # Gọi hàm draw_line_chart
    font=('Arial', 12, 'bold'),
    bg='#3cb371', # Màu xanh lá cây đẹp hơn
    fg='white',
    relief=tk.RAISED
)
open_button.pack(padx=20, pady=5)

# Khung chứa Biểu đồ
chart_frame = tk.Frame(root, bg='white', relief=tk.SUNKEN, bd=1)
chart_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=10)

# Chạy vòng lặp chính của GUI
root.mainloop()