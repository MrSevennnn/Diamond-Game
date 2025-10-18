# player_vs_ai.py - Chế độ người chơi đấu với AI

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from game import GameMap
from search import a_star
from heuristic import diamond_heuristic

class PlayerVsAIGame:
    """Chế độ đấu giữa người chơi và AI"""
    
    def __init__(self, parent, game_map):
        self.parent = parent
        self.game_map = game_map
        
        # Trạng thái game
        self.player_position = game_map.start
        self.player_diamonds = set()
        self.player_steps = 0
        self.player_start_time = None
        self.player_end_time = None
        self.game_active = False
        
        # AI result
        self.ai_result = None
        self.ai_start_time = None
        self.ai_end_time = None
        
        # UI settings
        self.cell_size = 35
        self.colors = {
            '.': 'white',
            '#': 'black',
            'player': 'yellow',
            'visited': 'lightgreen',
            'diamond_collected': 'lightblue'
        }
        
        self.create_game_window()
        self.reset_game()
    
    def create_game_window(self):
        """Tạo cửa sổ game"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Người chơi vs AI")
        self.window.geometry("1000x700")
        self.window.configure(bg='#f0f0f0')
        
        # Frame chính
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame trái - Điều khiển
        left_frame = ttk.LabelFrame(main_frame, text="Điều khiển", padding=10)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Frame phải - Game area
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # === ĐIỀU KHIỂN ===
        
        # Game controls
        control_frame = ttk.LabelFrame(left_frame, text="Trò chơi", padding=5)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(control_frame, text="Bắt đầu game mới", 
                  command=self.start_new_game).pack(fill='x', pady=2)
        ttk.Button(control_frame, text="Reset game", 
                  command=self.reset_game).pack(fill='x', pady=2)
        ttk.Button(control_frame, text="Chạy AI ngay", 
                  command=self.run_ai_immediately).pack(fill='x', pady=2)
        
        # Hướng dẫn di chuyển
        move_frame = ttk.LabelFrame(left_frame, text="Di chuyển", padding=5)
        move_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(move_frame, text="Sử dụng phím mũi tên:", font=('Arial', 9, 'bold')).pack()
        ttk.Label(move_frame, text="↑ : Lên", font=('Arial', 8)).pack(anchor='w')
        ttk.Label(move_frame, text="↓ : Xuống", font=('Arial', 8)).pack(anchor='w')
        ttk.Label(move_frame, text="← : Trái", font=('Arial', 8)).pack(anchor='w')
        ttk.Label(move_frame, text="→ : Phải", font=('Arial', 8)).pack(anchor='w')
        ttk.Label(move_frame, text="Enter: Hoàn thành", font=('Arial', 8)).pack(anchor='w')
        
        # Thống kê người chơi
        player_frame = ttk.LabelFrame(left_frame, text="Người chơi", padding=5)
        player_frame.pack(fill='x', pady=(0, 10))
        
        self.player_stats = ttk.Label(player_frame, text="Chưa bắt đầu", font=('Arial', 9))
        self.player_stats.pack()
        
        # Thống kê AI
        ai_frame = ttk.LabelFrame(left_frame, text="AI", padding=5)
        ai_frame.pack(fill='x', pady=(0, 10))
        
        self.ai_stats = ttk.Label(ai_frame, text="Chưa chạy", font=('Arial', 9))
        self.ai_stats.pack()
        
        # Kết quả
        result_frame = ttk.LabelFrame(left_frame, text="Kết quả", padding=5)
        result_frame.pack(fill='x')
        
        self.result_label = ttk.Label(result_frame, text="Chưa có kết quả", 
                                     font=('Arial', 10, 'bold'))
        self.result_label.pack()
        
        # === GAME AREA ===
        
        # Canvas frame
        canvas_frame = ttk.LabelFrame(right_frame, text="Bản đồ game", padding=5)
        canvas_frame.pack(fill='both', expand=True)
        
        # Canvas với scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='white', relief='sunken', bd=2)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind keyboard events
        self.window.bind('<Key>', self.on_key_press)
        self.window.focus_set()
        
        # Đường đi của người chơi
        self.player_path = []
        
    def reset_game(self):
        """Reset game về trạng thái ban đầu"""
        self.player_position = self.game_map.start
        self.player_diamonds = set()
        self.player_steps = 0
        self.player_start_time = None
        self.player_end_time = None
        self.game_active = False
        self.player_path = [self.player_position]
        
        self.ai_result = None
        self.ai_start_time = None
        self.ai_end_time = None
        
        self.update_display()
        self.update_stats()
        
    def start_new_game(self):
        """Bắt đầu game mới"""
        self.reset_game()
        self.game_active = True
        self.player_start_time = time.time()
        
        messagebox.showinfo("Bắt đầu!", 
                           "Game đã bắt đầu!\n"
                           "Sử dụng phím mũi tên để di chuyển.\n"
                           "Thu thập tất cả kim cương và đến đích.\n"
                           "Nhấn Enter khi hoàn thành.")
        
        self.update_stats()
        
    def on_key_press(self, event):
        """Xử lý phím bấm"""
        if not self.game_active:
            return
            
        key = event.keysym
        new_position = None
        
        # Xác định vị trí mới
        row, col = self.player_position
        if key == 'Up':
            new_position = (row - 1, col)
        elif key == 'Down':
            new_position = (row + 1, col)
        elif key == 'Left':
            new_position = (row, col - 1)
        elif key == 'Right':
            new_position = (row, col + 1)
        elif key == 'Return':  # Enter key
            self.finish_game()
            return
        
        # Kiểm tra di chuyển hợp lệ
        if new_position and self.game_map.is_valid_position(new_position):
            self.player_position = new_position
            self.player_steps += 1
            self.player_path.append(new_position)
            
            # Thu thập kim cương
            if new_position in self.game_map.diamonds:
                self.player_diamonds.add(new_position)
            
            # Kiểm tra hoàn thành tự động
            if (new_position == self.game_map.goal and 
                len(self.player_diamonds) == len(self.game_map.diamonds)):
                self.finish_game()
                return
            
            self.update_display()
            self.update_stats()
        
    def finish_game(self):
        """Hoàn thành game người chơi"""
        if not self.game_active:
            return
            
        self.game_active = False
        self.player_end_time = time.time()
        
        # Kiểm tra điều kiện thắng
        if (self.player_position == self.game_map.goal and 
            len(self.player_diamonds) == len(self.game_map.diamonds)):
            messagebox.showinfo("Hoàn thành!", "Bạn đã hoàn thành game!")
        else:
            messagebox.showwarning("Chưa hoàn thành!", 
                                 "Bạn chưa thu thập đủ kim cương hoặc chưa đến đích!")
        
        # Chạy AI để so sánh
        self.run_ai()
        
    def run_ai_immediately(self):
        """Chạy AI ngay lập tức để tham khảo"""
        self.run_ai()
        
    def run_ai(self):
        """Chạy AI để tìm lời giải"""
        def run_ai_thread():
            try:
                self.ai_start_time = time.time()
                self.ai_result = a_star(self.game_map, diamond_heuristic)
                self.ai_end_time = time.time()
                
                # Cập nhật UI trong main thread
                self.window.after(0, self.show_comparison)
                
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Lỗi AI", f"Lỗi chạy AI: {e}"))
        
        threading.Thread(target=run_ai_thread, daemon=True).start()
        
    def show_comparison(self):
        """Hiển thị so sánh kết quả"""
        self.update_stats()
        
        if not self.ai_result or not self.ai_result.found_solution:
            messagebox.showerror("Lỗi", "AI không tìm được lời giải!")
            return
            
        # Tính toán kết quả
        player_time = 0
        if self.player_start_time and self.player_end_time:
            player_time = self.player_end_time - self.player_start_time
        
        ai_time = self.ai_end_time - self.ai_start_time if self.ai_start_time and self.ai_end_time else 0
        
        player_completed = (len(self.player_diamonds) == len(self.game_map.diamonds) and 
                          self.player_position == self.game_map.goal)
        
        # Tạo cửa sổ so sánh
        self.show_detailed_comparison(player_time, ai_time, player_completed)
        
    def show_detailed_comparison(self, player_time, ai_time, player_completed):
        """Hiển thị so sánh chi tiết"""
        comparison_window = tk.Toplevel(self.window)
        comparison_window.title("So sánh kết quả")
        comparison_window.geometry("500x400")
        comparison_window.configure(bg='white')
        
        # Main frame
        main_frame = ttk.Frame(comparison_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="KẾT QUẢ SO SÁNH", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Player results
        player_frame = ttk.LabelFrame(main_frame, text="Người chơi", padding=10)
        player_frame.pack(fill='x', pady=5)
        
        player_status = "Hoàn thành" if player_completed else "Chưa hoàn thành"
        player_info = (f"Trạng thái: {player_status}\n"
                      f"Thời gian: {player_time:.1f}s\n"
                      f"Số bước: {self.player_steps}\n"
                      f"Kim cương: {len(self.player_diamonds)}/{len(self.game_map.diamonds)}")
        
        ttk.Label(player_frame, text=player_info, font=('Arial', 10)).pack(anchor='w')
        
        # AI results
        ai_frame = ttk.LabelFrame(main_frame, text="AI (A*)", padding=10)
        ai_frame.pack(fill='x', pady=5)
        
        ai_info = (f"Trạng thái: Hoàn thành\n"
                  f"Thời gian: {ai_time:.3f}s\n"
                  f"Số bước: {self.ai_result.cost}\n"
                  f"Kim cương: {len(self.game_map.diamonds)}/{len(self.game_map.diamonds)}\n"
                  f"Node duyệt: {self.ai_result.nodes_explored}")
        
        ttk.Label(ai_frame, text=ai_info, font=('Arial', 10)).pack(anchor='w')
        
        # Result
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill='x', pady=10)
        
        # Xác định người thắng
        if not player_completed:
            winner = "AI thắng (Người chơi chưa hoàn thành)"
            color = 'red'
        elif self.player_steps < self.ai_result.cost:
            winner = "Người chơi thắng (Ít bước hơn)!"
            color = 'green'
        elif self.player_steps == self.ai_result.cost:
            if player_time < ai_time:
                winner = "Người chơi thắng (Nhanh hơn)!"
                color = 'green'
            else:
                winner = "🤖 AI thắng (Nhanh hơn)"
                color = 'blue'
        else:
            winner = "🤖 AI thắng (Ít bước hơn)"
            color = 'blue'
        
        result_label = tk.Label(result_frame, text=winner, 
                               font=('Arial', 14, 'bold'), fg=color)
        result_label.pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="🔄 Chơi lại", 
                  command=lambda: [comparison_window.destroy(), self.start_new_game()]).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="👁️ Xem lời giải AI", 
                  command=lambda: [comparison_window.destroy(), self.show_ai_solution()]).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="✅ Đóng", 
                  command=comparison_window.destroy).pack(side='right', padx=5)
        
    def show_ai_solution(self):
        """Hiển thị lời giải của AI"""
        if self.ai_result and self.ai_result.found_solution:
            # Tạo cửa sổ mới để hiển thị lời giải AI
            ai_window = tk.Toplevel(self.window)
            ai_window.title("🤖 Lời giải AI")
            ai_window.geometry("600x500")
            
            # Canvas để vẽ lời giải
            canvas = tk.Canvas(ai_window, bg='white')
            canvas.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Vẽ bản đồ với lời giải AI
            self.draw_ai_solution(canvas)
    
    def draw_ai_solution(self, canvas):
        """Vẽ lời giải AI lên canvas"""
        if not self.ai_result or not self.ai_result.found_solution:
            return
            
        rows, cols = self.game_map.rows, self.game_map.cols
        canvas_width = cols * self.cell_size
        canvas_height = rows * self.cell_size
        
        canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # Vẽ bản đồ cơ bản
        for i in range(rows):
            for j in range(cols):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                cell_type = self.game_map.grid[i][j]
                color = 'white' if cell_type == '.' else 'black'
                
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')
        
        # Vẽ đường đi AI
        path = self.ai_result.path
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            
            x1 = c1 * self.cell_size + self.cell_size // 2
            y1 = r1 * self.cell_size + self.cell_size // 2
            x2 = c2 * self.cell_size + self.cell_size // 2
            y2 = r2 * self.cell_size + self.cell_size // 2
            
            canvas.create_line(x1, y1, x2, y2, fill='blue', width=3)
        
        # Vẽ các điểm đặc biệt
        self.draw_special_points(canvas)
    
    def draw_special_points(self, canvas):
        """Vẽ start, goal, diamonds"""
        # Start
        if self.game_map.start:
            row, col = self.game_map.start
            x, y = col * self.cell_size, row * self.cell_size
            canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                  fill='green', outline='darkgreen', width=2)
            canvas.create_text(x + self.cell_size//2, y + self.cell_size//2,
                              text='S', fill='white', font=('Arial', 12, 'bold'))
        
        # Goal
        if self.game_map.goal:
            row, col = self.game_map.goal
            x, y = col * self.cell_size, row * self.cell_size
            canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                  fill='red', outline='darkred', width=2)
            canvas.create_text(x + self.cell_size//2, y + self.cell_size//2,
                              text='G', fill='white', font=('Arial', 12, 'bold'))
        
        # Diamonds
        for diamond in self.game_map.diamonds:
            row, col = diamond
            x, y = col * self.cell_size, row * self.cell_size
            canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                  fill='cyan', outline='blue', width=2)
            canvas.create_text(x + self.cell_size//2, y + self.cell_size//2,
                              text='D', fill='blue', font=('Arial', 12, 'bold'))
    
    def update_display(self):
        """Cập nhật hiển thị bản đồ"""
        self.canvas.delete("all")
        
        rows, cols = self.game_map.rows, self.game_map.cols
        canvas_width = cols * self.cell_size
        canvas_height = rows * self.cell_size
        
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # Vẽ bản đồ cơ bản
        for i in range(rows):
            for j in range(cols):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                cell_type = self.game_map.grid[i][j]
                
                # Xác định màu
                color = 'white'
                if cell_type == '#':
                    color = 'black'
                elif (i, j) in self.player_path[:-1]:  # Đường đã đi (trừ vị trí hiện tại)
                    color = 'lightgreen'
                
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                           fill=color, outline='gray', width=1)
        
        # Vẽ đường đi của người chơi
        if len(self.player_path) > 1:
            for i in range(len(self.player_path) - 1):
                r1, c1 = self.player_path[i]
                r2, c2 = self.player_path[i + 1]
                
                x1 = c1 * self.cell_size + self.cell_size // 2
                y1 = r1 * self.cell_size + self.cell_size // 2
                x2 = c2 * self.cell_size + self.cell_size // 2
                y2 = r2 * self.cell_size + self.cell_size // 2
                
                self.canvas.create_line(x1, y1, x2, y2, fill='orange', width=2)
        
        # Vẽ các điểm đặc biệt
        self.draw_special_points(self.canvas)
        
        # Vẽ vị trí người chơi
        row, col = self.player_position
        x, y = col * self.cell_size, row * self.cell_size
        self.canvas.create_oval(x + 5, y + 5, x + self.cell_size - 5, y + self.cell_size - 5,
                               fill='yellow', outline='orange', width=3)
        self.canvas.create_text(x + self.cell_size//2, y + self.cell_size//2,
                               text='P', fill='red', font=('Arial', 12, 'bold'))
        
        # Đánh dấu kim cương đã thu thập
        for diamond in self.player_diamonds:
            row, col = diamond
            x, y = col * self.cell_size, row * self.cell_size
            self.canvas.create_rectangle(x + 2, y + 2, x + self.cell_size - 2, y + self.cell_size - 2,
                                       fill='lightblue', outline='green', width=2)
            self.canvas.create_text(x + self.cell_size//2, y + self.cell_size//2,
                                   text='✓', fill='green', font=('Arial', 10, 'bold'))
    
    def update_stats(self):
        """Cập nhật thống kê"""
        # Player stats
        if self.game_active and self.player_start_time:
            current_time = time.time() - self.player_start_time
            player_text = (f"Thời gian: {current_time:.1f}s\n"
                          f"Bước đi: {self.player_steps}\n"
                          f"Kim cương: {len(self.player_diamonds)}/{len(self.game_map.diamonds)}\n"
                          f"Vị trí: {self.player_position}")
        elif self.player_end_time and self.player_start_time:
            total_time = self.player_end_time - self.player_start_time
            player_text = (f"Hoàn thành: {total_time:.1f}s\n"
                          f"Bước đi: {self.player_steps}\n"
                          f"Kim cương: {len(self.player_diamonds)}/{len(self.game_map.diamonds)}")
        else:
            player_text = "Chưa bắt đầu"
        
        self.player_stats.config(text=player_text)
        
        # AI stats
        if self.ai_result:
            ai_time = self.ai_end_time - self.ai_start_time if self.ai_start_time and self.ai_end_time else 0
            ai_text = (f"Thời gian: {ai_time:.3f}s\n"
                      f"Bước đi: {self.ai_result.cost}\n"
                      f"Kim cương: {len(self.game_map.diamonds)}/{len(self.game_map.diamonds)}\n"
                      f"Node duyệt: {self.ai_result.nodes_explored}")
        else:
            ai_text = "Chưa chạy"
        
        self.ai_stats.config(text=ai_text)
        
        # Result comparison
        if self.ai_result and self.player_end_time:
            player_completed = (len(self.player_diamonds) == len(self.game_map.diamonds) and 
                              self.player_position == self.game_map.goal)
            
            if not player_completed:
                result_text = "🤖 AI thắng"
                self.result_label.config(foreground='blue')
            elif self.player_steps < self.ai_result.cost:
                result_text = "👤 Người chơi thắng!"
                self.result_label.config(foreground='green')
            elif self.player_steps == self.ai_result.cost:
                result_text = "🤝 Hòa!"
                self.result_label.config(foreground='orange')
            else:
                result_text = "🤖 AI thắng"
                self.result_label.config(foreground='blue')
        else:
            result_text = "Chưa có kết quả"
            self.result_label.config(foreground='black')
            
        self.result_label.config(text=result_text)