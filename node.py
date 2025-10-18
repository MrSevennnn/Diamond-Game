# node.py - Lớp Node đại diện cho trạng thái trong trò chơi Kim cương

class Node:
    """
    Lớp Node đại diện cho một trạng thái trong trò chơi Kim cương
    """
    
    def __init__(self, position, diamonds_collected=frozenset(), g_cost=0, h_cost=0, parent=None):
        """
        Khởi tạo node
        Args:
            position (tuple): vị trí (row, col) của tác tử
            diamonds_collected (frozenset): tập hợp kim cương đã thu thập
            g_cost (int): chi phí từ điểm bắt đầu đến node hiện tại
            h_cost (float): giá trị heuristic từ node hiện tại đến đích
            parent (Node): node cha
        """
        self.position = position
        self.diamonds_collected = diamonds_collected
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent
    
    @property
    def f_cost(self):
        """Tổng chi phí f = g + h (dùng cho A*)"""
        return self.g_cost + self.h_cost
    
    def __eq__(self, other):
        """So sánh hai node"""
        if not isinstance(other, Node):
            return False
        return (self.position == other.position and 
                self.diamonds_collected == other.diamonds_collected)
    
    def __hash__(self):
        """Hash để sử dụng trong set và dict"""
        return hash((self.position, self.diamonds_collected))
    
    def __lt__(self, other):
        """So sánh để sử dụng trong priority queue"""
        return self.f_cost < other.f_cost
    
    def __repr__(self):
        """Hiển thị thông tin node"""
        return f"Node(pos={self.position}, diamonds={len(self.diamonds_collected)}, g={self.g_cost}, h={self.h_cost:.2f})"
    
    def get_path(self):
        """Lấy đường đi từ root đến node hiện tại"""
        path = []
        current = self
        while current:
            path.append(current.position)
            current = current.parent
        return path[::-1]  # Đảo ngược để có path từ start đến goal