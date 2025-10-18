# game.py - Lớp GameMap quản lý bản đồ và logic trò chơi

class GameMap:
    """
    Lớp quản lý bản đồ và logic trò chơi Kim cương
    """
    
    def __init__(self, map_file):
        """
        Khởi tạo bản đồ từ file
        Args:
            map_file (str): đường dẫn đến file map
        """
        self.grid = []
        self.start = None
        self.goal = None
        self.diamonds = set()
        self.rows = 0
        self.cols = 0
        
        self.load_map(map_file)
    
    def load_map(self, map_file):
        """
        Đọc bản đồ từ file
        Args:
            map_file (str): đường dẫn đến file map
        """
        try:
            with open(map_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.grid = [list(line.strip()) for line in lines if line.strip()]
            self.rows = len(self.grid)
            self.cols = len(self.grid[0]) if self.rows > 0 else 0
            
            # Tìm vị trí start, goal và diamonds
            for i in range(self.rows):
                for j in range(self.cols):
                    cell = self.grid[i][j]
                    if cell == 'S':
                        self.start = (i, j)
                        self.grid[i][j] = '.'  # Thay thế S bằng ô trống
                    elif cell == 'G':
                        self.goal = (i, j)
                        self.grid[i][j] = '.'  # Thay thế G bằng ô trống
                    elif cell == 'D':
                        self.diamonds.add((i, j))
                        self.grid[i][j] = '.'  # Thay thế D bằng ô trống
            
            if not self.start:
                raise ValueError("Không tìm thấy điểm bắt đầu (S) trong bản đồ")
            if not self.goal:
                raise ValueError("Không tìm thấy điểm đích (G) trong bản đồ")
                
        except FileNotFoundError:
            print(f"Không tìm thấy file: {map_file}")
            raise
        except Exception as e:
            print(f"Lỗi đọc file map: {e}")
            raise
    
    def is_valid_position(self, position):
        """
        Kiểm tra vị trí có hợp lệ không
        Args:
            position (tuple): vị trí (row, col)
        Returns:
            bool: True nếu vị trí hợp lệ
        """
        row, col = position
        return (0 <= row < self.rows and 
                0 <= col < self.cols and 
                self.grid[row][col] != '#')
    
    def get_neighbors(self, position):
        """
        Lấy danh sách các vị trí láng giềng hợp lệ
        Args:
            position (tuple): vị trí hiện tại (row, col)
        Returns:
            list: danh sách các vị trí láng giềng hợp lệ
        """
        row, col = position
        neighbors = []
        
        # 4 hướng di chuyển: lên, xuống, trái, phải
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            new_position = (new_row, new_col)
            
            if self.is_valid_position(new_position):
                neighbors.append(new_position)
        
        return neighbors
    
    def is_goal_state(self, position, diamonds_collected):
        """
        Kiểm tra có phải trạng thái đích không
        Args:
            position (tuple): vị trí hiện tại
            diamonds_collected (set): tập kim cương đã thu thập
        Returns:
            bool: True nếu là trạng thái đích
        """
        return (position == self.goal and 
                len(diamonds_collected) == len(self.diamonds))
    
    def collect_diamond(self, position, diamonds_collected):
        """
        Thu thập kim cương tại vị trí hiện tại (nếu có)
        Args:
            position (tuple): vị trí hiện tại
            diamonds_collected (set): tập kim cương đã thu thập
        Returns:
            frozenset: tập kim cương sau khi thu thập
        """
        new_diamonds = set(diamonds_collected)
        if position in self.diamonds:
            new_diamonds.add(position)
        return frozenset(new_diamonds)
    
    def display_map(self, path=None, current_pos=None):
        """
        Hiển thị bản đồ với đường đi (nếu có)
        Args:
            path (list): đường đi cần hiển thị
            current_pos (tuple): vị trí hiện tại
        """
        # Tạo bản sao bản đồ để hiển thị
        display_grid = [row[:] for row in self.grid]
        
        # Đánh dấu start, goal, diamonds
        if self.start:
            display_grid[self.start[0]][self.start[1]] = 'S'
        if self.goal:
            display_grid[self.goal[0]][self.goal[1]] = 'G'
        for diamond in self.diamonds:
            display_grid[diamond[0]][diamond[1]] = 'D'
        
        # Đánh dấu đường đi
        if path:
            for i, pos in enumerate(path):
                row, col = pos
                if pos == self.start:
                    display_grid[row][col] = 'S'
                elif pos == self.goal:
                    display_grid[row][col] = 'G'
                elif pos in self.diamonds:
                    display_grid[row][col] = 'D'
                elif display_grid[row][col] == '.':
                    display_grid[row][col] = '*'
        
        # Đánh dấu vị trí hiện tại
        if current_pos:
            row, col = current_pos
            display_grid[row][col] = '@'
        
        # In bản đồ
        print("\n" + "="*50)
        for row in display_grid:
            print(' '.join(row))
        print("="*50)
    
    def get_map_info(self):
        """
        Lấy thông tin tổng quan về bản đồ
        Returns:
            dict: thông tin bản đồ
        """
        return {
            'rows': self.rows,
            'cols': self.cols,
            'start': self.start,
            'goal': self.goal,
            'diamonds_count': len(self.diamonds),
            'diamonds_positions': list(self.diamonds)
        }