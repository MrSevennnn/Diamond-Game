# gui.py - Giao diện đồ họa cho trò chơi Kim cương

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from game import GameMap
from search import (bfs, dfs, ucs, greedy_best_first, a_star, compare_algorithms)
from heuristic import diamond_heuristic

class DiamondGameGUI:
    """Giao diện đồ họa cho trò chơi Kim cương"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Trò chơi Kim cương - Diamond Game")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Biến lưu trữ
        self.game_map = None
        self.current_result = None
        self.cell_size = 30
        
        # Màu sắc
        self.colors = {
            '.': 'white',
            '#': 'black', 
            'S': 'green',
            'G': 'red',
            'D': 'cyan',
            '*': 'orange',
            '@': 'yellow'
        }
        
        self.create_widgets()
        self.load_selected_map()
    
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        
        # Frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame trái - Điều khiển
        left_frame = ttk.LabelFrame(main_frame, text="Điều khiển", padding=10)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Frame phải - Hiển thị bản đồ và kết quả
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # === FRAME TRÁI - ĐIỀU KHIỂN ===
        
        # Nhóm File
        file_frame = ttk.LabelFrame(left_frame, text="Chọn bản đồ", padding=5)
        file_frame.pack(fill='x', pady=(0, 10))
        
        # Combobox chọn bản đồ
        self.map_var = tk.StringVar()
        self.map_combobox = ttk.Combobox(file_frame, textvariable=self.map_var, 
                                        values=["Simple", "Medium", "Complex"],
                                        state="readonly", width=20)
        self.map_combobox.set("Simple")  # Mặc định chọn Simple
        self.map_combobox.bind("<<ComboboxSelected>>", self.on_map_selection_change)
        self.map_combobox.pack(fill='x', pady=2)
        
        # Thông tin bản đồ
        info_frame = ttk.LabelFrame(left_frame, text="Thông tin bản đồ", padding=5)
        info_frame.pack(fill='x', pady=(0, 10))
        
        self.info_label = ttk.Label(info_frame, text="Chưa tải bản đồ", 
                                   font=('Arial', 9))
        self.info_label.pack()
        
        # Nhóm thuật toán
        algo_frame = ttk.LabelFrame(left_frame, text="Thuật toán tìm kiếm", padding=5)
        algo_frame.pack(fill='x', pady=(0, 10))
        
        algorithms = [
            ("BFS", "bfs"),
            ("DFS", "dfs"), 
            ("UCS", "ucs"),
            ("Greedy", "greedy"),
            ("A*", "astar")
        ]
        
        for name, key in algorithms:
            ttk.Button(algo_frame, text=name, width=15,
                      command=lambda k=key: self.run_algorithm(k)).pack(fill='x', pady=1)
        
        ttk.Separator(algo_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Button(algo_frame, text="So sánh tất cả", 
                  command=self.compare_all_algorithms).pack(fill='x', pady=2)
        ttk.Button(algo_frame, text="Người chơi vs AI", 
                  command=self.start_player_vs_ai).pack(fill='x', pady=2)
        
        # Nhóm hiển thị
        display_frame = ttk.LabelFrame(left_frame, text="Hiển thị", padding=5)
        display_frame.pack(fill='x', pady=(0, 10))
        
        self.show_path_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Hiện đường đi", 
                       variable=self.show_path_var,
                       command=self.update_map_display).pack(anchor='w')
        
        self.show_numbers_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(display_frame, text="Hiện số thứ tự", 
                       variable=self.show_numbers_var,
                       command=self.update_map_display).pack(anchor='w')
        
        ttk.Button(display_frame, text="Làm mới bản đồ", 
                  command=self.refresh_map).pack(fill='x', pady=2)
        
        # Nhóm kết quả
        result_frame = ttk.LabelFrame(left_frame, text="Xuất kết quả", padding=5)
        result_frame.pack(fill='x')
        
        ttk.Button(result_frame, text="Lưu kết quả", 
                  command=self.save_results).pack(fill='x', pady=2)
        ttk.Button(result_frame, text="Hướng dẫn", 
                  command=self.show_help).pack(fill='x', pady=2)
        
        # === FRAME PHẢI - HIỂN THỊ ===
        
        # Frame bản đồ
        map_frame = ttk.LabelFrame(right_frame, text="Bản đồ trò chơi", padding=5)
        map_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Canvas để vẽ bản đồ
        canvas_frame = ttk.Frame(map_frame)
        canvas_frame.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', relief='sunken', bd=2)
        
        # Thanh cuộn
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack canvas và scrollbars
        self.canvas.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Frame kết quả
        result_frame = ttk.LabelFrame(right_frame, text="Kết quả tìm kiếm", padding=5)
        result_frame.pack(fill='x')
        
        # Text widget để hiển thị kết quả
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.result_text = tk.Text(text_frame, height=10, wrap='word', font=('Courier', 10))
        result_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side='left', fill='both', expand=True)
        result_scrollbar.pack(side='right', fill='y')
        
        # Progress bar
        self.progress = ttk.Progressbar(right_frame, mode='indeterminate')
        
    def load_selected_map(self):
        """Tải bản đồ được chọn từ combobox"""
        try:
            map_name = self.map_var.get() if hasattr(self, 'map_var') else "Simple"
            map_files = {
                "Simple": "map_simple.txt",
                "Medium": "map_medium.txt", 
                "Complex": "map_complex.txt"
            }
            
            map_file = map_files.get(map_name, "map_simple.txt")
            self.game_map = GameMap(map_file)
            self.update_map_info()
            self.draw_map()
            self.clear_results()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải bản đồ {map_name}: {e}")
    
    def on_map_selection_change(self, event=None):
        """Xử lý khi người dùng thay đổi lựa chọn bản đồ"""
        self.load_selected_map()
    
    def update_map_info(self):
        """Cập nhật thông tin bản đồ"""
        if self.game_map:
            info = self.game_map.get_map_info()
            text = (f"Kích thước: {info['rows']}x{info['cols']}\n"
                   f"Điểm bắt đầu: {info['start']}\n"
                   f"Điểm đích: {info['goal']}\n" 
                   f"Kim cương: {info['diamonds_count']}")
            self.info_label.config(text=text)
    
    def draw_map(self):
        """Vẽ bản đồ lên canvas"""
        if not self.game_map:
            return
        
        self.canvas.delete("all")
        
        rows, cols = self.game_map.rows, self.game_map.cols
        canvas_width = cols * self.cell_size
        canvas_height = rows * self.cell_size
        
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # Vẽ lưới và các ô
        for i in range(rows):
            for j in range(cols):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                # Xác định màu và ký hiệu
                cell_type = self.game_map.grid[i][j]
                color = self.colors.get(cell_type, 'white')
                
                # Vẽ ô
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                           fill=color, outline='gray', width=1)
                
                # Thêm ký hiệu đặc biệt
                text = ""
                text_color = "black"
                
                if (i, j) == self.game_map.start:
                    text = "S"
                    text_color = "green"
                elif (i, j) == self.game_map.goal:
                    text = "G"  
                    text_color = "red"
                elif (i, j) in self.game_map.diamonds:
                    text = "D"
                    text_color = "blue"
                
                if text:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                          text=text, fill=text_color, font=('Arial', 12, 'bold'))
        
        # Vẽ đường đi nếu có
        if self.current_result and self.current_result.found_solution and self.show_path_var.get():
            self.draw_path(self.current_result.path)
    
    def draw_path(self, path):
        """Vẽ đường đi lên canvas"""
        if len(path) < 2:
            return
        
        # Vẽ đường nối
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            
            x1 = c1 * self.cell_size + self.cell_size // 2
            y1 = r1 * self.cell_size + self.cell_size // 2
            x2 = c2 * self.cell_size + self.cell_size // 2
            y2 = r2 * self.cell_size + self.cell_size // 2
            
            self.canvas.create_line(x1, y1, x2, y2, fill='orange', width=3)
        
        # Vẽ điểm trên đường đi
        for i, (row, col) in enumerate(path):
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            
            # Không vẽ đè lên start và goal
            if (row, col) not in [self.game_map.start, self.game_map.goal]:
                self.canvas.create_oval(x-4, y-4, x+4, y+4, 
                                      fill='orange', outline='darkorange', width=2)
        
        # Hiển thị số thứ tự nếu được chọn - tránh trùng lặp
        if self.show_numbers_var.get():
            # Tạo dictionary để lưu tất cả số thứ tự cho mỗi vị trí
            position_numbers = {}
            for i, (row, col) in enumerate(path):
                if i > 0 and i < len(path) - 1:  # Không hiển thị số cho start và goal
                    pos = (row, col)
                    if pos not in position_numbers:
                        position_numbers[pos] = []
                    position_numbers[pos].append(i)
            
            # Vẽ số thứ tự
            for (row, col), numbers in position_numbers.items():
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                
                if len(numbers) == 1:
                    # Chỉ có 1 số - hiển thị bình thường
                    self.canvas.create_text(x+12, y-12, text=str(numbers[0]), 
                                          fill='purple', font=('Arial', 8, 'bold'))
                else:
                    # Có nhiều số - hiển thị danh sách
                    text = ','.join(map(str, numbers))
                    # Tạo nền trắng cho text dài
                    self.canvas.create_rectangle(x+5, y-20, x+5+len(text)*4, y-5,
                                               fill='white', outline='purple', width=1)
                    self.canvas.create_text(x+12, y-12, text=text, 
                                          fill='purple', font=('Arial', 7, 'bold'))
    
    def update_map_display(self):
        """Cập nhật hiển thị bản đồ"""
        self.draw_map()
    
    def refresh_map(self):
        """Làm mới hiển thị bản đồ"""
        self.current_result = None
        self.draw_map()
        self.clear_results()
    
    def run_algorithm(self, algorithm_name):
        """Chạy một thuật toán cụ thể"""
        if not self.game_map:
            messagebox.showerror("Lỗi", "Vui lòng tải bản đồ trước!")
            return
        
        # Hiển thị progress bar
        self.progress.pack(fill='x', pady=5)
        self.progress.start()
        
        # Chạy thuật toán trong thread riêng để không block UI
        def run_algo():
            try:
                algorithms = {
                    'bfs': bfs,
                    'dfs': dfs,
                    'ucs': ucs,
                    'greedy': greedy_best_first,
                    'astar': a_star
                }
                
                result = algorithms[algorithm_name](self.game_map)
                
                # Cập nhật UI trong main thread
                self.root.after(0, self.update_result, result)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi chạy thuật toán: {e}"))
            finally:
                self.root.after(0, self.stop_progress)
        
        threading.Thread(target=run_algo, daemon=True).start()
    
    def compare_all_algorithms(self):
        """So sánh tất cả các thuật toán"""
        if not self.game_map:
            messagebox.showerror("Lỗi", "Vui lòng tải bản đồ trước!")
            return
        
        self.progress.pack(fill='x', pady=5)
        self.progress.start()
        
        def run_comparison():
            try:
                results = compare_algorithms(self.game_map)
                self.root.after(0, self.display_comparison_results, results)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi so sánh thuật toán: {e}"))
            finally:
                self.root.after(0, self.stop_progress)
        
        threading.Thread(target=run_comparison, daemon=True).start()
    
    def update_result(self, result):
        """Cập nhật kết quả lên giao diện"""
        self.current_result = result
        
        # Hiển thị kết quả trong text widget
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, str(result))
        
        # Vẽ lại bản đồ với đường đi
        self.draw_map()
        
        # Hiển thị thông báo
        if result.found_solution:
            messagebox.showinfo("Thành công", 
                              f"Tìm thấy lời giải!\nChi phí: {result.cost}\n"
                              f"Thời gian: {result.execution_time:.4f}s")
        else:
            messagebox.showwarning("Không tìm thấy", "Không tìm thấy lời giải!")
    
    def display_comparison_results(self, results):
        """Hiển thị kết quả so sánh"""
        self.result_text.delete(1.0, tk.END)
        
        # Header
        self.result_text.insert(tk.END, "="*80 + "\n")
        self.result_text.insert(tk.END, "KẾT QUẢ SO SÁNH CÁC THUẬT TOÁN\n")
        self.result_text.insert(tk.END, "="*80 + "\n\n")
        
        # Bảng so sánh
        header = f"{'Thuật toán':<15} {'Kết quả':<8} {'Chi phí':<8} {'Node':<8} {'Thời gian(s)':<12}\n"
        self.result_text.insert(tk.END, header)
        self.result_text.insert(tk.END, "-" * 60 + "\n")
        
        best_result = None
        for name, result in results.items():
            if result.found_solution:
                status = "✓"
                cost = result.cost
                if not best_result or result.cost < best_result.cost:
                    best_result = result
            else:
                status = "✗"
                cost = "-"
            
            row = f"{name:<15} {status:<8} {cost:<8} {result.nodes_explored:<8} {result.execution_time:<12.4f}\n"
            self.result_text.insert(tk.END, row)
        
        self.result_text.insert(tk.END, "\n" + "="*60 + "\n")
        
        # Hiển thị thuật toán tốt nhất
        if best_result:
            self.result_text.insert(tk.END, f"\nTHUẬT TOÁN TỐT NHẤT: {best_result.algorithm}\n")
            self.current_result = best_result
            self.draw_map()
    
    def stop_progress(self):
        """Dừng progress bar"""
        self.progress.stop()
        self.progress.pack_forget()
    
    def clear_results(self):
        """Xóa kết quả hiện tại"""
        self.result_text.delete(1.0, tk.END)
        self.current_result = None
    
    def save_results(self):
        """Lưu kết quả ra file"""
        if not self.current_result:
            messagebox.showwarning("Chưa có kết quả", "Vui lòng chạy thuật toán trước!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Lưu kết quả",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(self.current_result))
                    if self.current_result.found_solution:
                        f.write(f"\n\nĐường đi chi tiết:\n")
                        for i, pos in enumerate(self.current_result.path):
                            f.write(f"Bước {i+1}: {pos}\n")
                
                messagebox.showinfo("Thành công", f"Đã lưu kết quả vào: {file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
    
    def start_player_vs_ai(self):
        """Khởi chạy chế độ người chơi vs AI"""
        if not self.game_map:
            messagebox.showerror("Lỗi", "Vui lòng tải bản đồ trước!")
            return
        
        try:
            from player_vs_ai import PlayerVsAIGame
            PlayerVsAIGame(self.root, self.game_map)
        except ImportError:
            messagebox.showerror("Lỗi", "Không thể tải module player_vs_ai!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khởi chạy chế độ đấu: {e}")

    def show_help(self):
        """Hiển thị hướng dẫn sử dụng"""
        help_text = """
HƯỚNG DẪN SỬ DỤNG TRÒ CHƠI KIM CƯƠNG

MỤC TIÊU:
Thu thập tất cả kim cương (D) và đến vị trí đích (G) với chi phí tối thiểu.

KÝ HIỆU:
• S: Điểm bắt đầu (màu xanh lá)
• D: Kim cương (màu cyan) 
• G: Điểm đích (màu đỏ)
• #: Tường (màu đen)
• .: Ô trống (màu trắng)
• Đường cam: Đường đi tìm được

CÁCH SỬ DỤNG:
1. Tải bản đồ bằng nút "Mở file bản đồ"
2. Chọn thuật toán muốn chạy HOẶC
3. Chọn "Người chơi vs AI" để đấu với máy tính
4. Xem kết quả trên bản đồ và bảng kết quả
5. Sử dụng "So sánh tất cả" để thấy hiệu suất các thuật toán

CHẾ ĐỘ NGƯỜI CHƠI VS AI:
• Sử dụng phím mũi tên để di chuyển
• Thu thập tất cả kim cương và đến đích
• AI sẽ tự động chạy khi bạn hoàn thành
• So sánh kết quả: thời gian, số bước, hiệu quả

TÍNH NĂNG:
• Hiển thị/ẩn đường đi và số thứ tự bước
• Lưu kết quả ra file
• So sánh hiệu suất các thuật toán
• Chế độ đấu tương tác với AI

CÁC THUẬT TOÁN:
• BFS: Tìm kiếm theo chiều rộng - đảm bảo tối ưu
• DFS: Tìm kiếm theo chiều sâu - tiết kiệm bộ nhớ  
• UCS: Chi phí đồng nhất - tối ưu về chi phí
• Greedy: Tham lam - nhanh nhưng không đảm bảo tối ưu
• A*: Cân bằng tốc độ và tối ưu
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Hướng dẫn sử dụng")
        help_window.geometry("600x500")
        help_window.configure(bg='white')
        
        text_widget = tk.Text(help_window, wrap='word', font=('Arial', 10), 
                             bg='white', fg='black', padx=20, pady=20)
        scrollbar = ttk.Scrollbar(help_window, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        text_widget.insert(1.0, help_text)
        text_widget.config(state='disabled')

def main():
    """Hàm chính khởi chạy giao diện"""
    root = tk.Tk()
    app = DiamondGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()