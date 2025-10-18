# heuristic.py - Các hàm heuristic cho thuật toán tìm kiếm

import math

def manhattan_distance(pos1, pos2):
    """
    Tính khoảng cách Manhattan giữa hai điểm
    Args:
        pos1 (tuple): vị trí đầu tiên (row, col)
        pos2 (tuple): vị trí thứ hai (row, col)
    Returns:
        int: khoảng cách Manhattan
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def euclidean_distance(pos1, pos2):
    """
    Tính khoảng cách Euclidean giữa hai điểm
    Args:
        pos1 (tuple): vị trí đầu tiên (row, col)
        pos2 (tuple): vị trí thứ hai (row, col)
    Returns:
        float: khoảng cách Euclidean
    """
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def diamond_heuristic(node, game_map):
    """
    Hàm heuristic chính cho trò chơi Kim cương
    Tính khoảng cách đến kim cương gần nhất + khoảng cách đến goal
    
    Args:
        node (Node): node hiện tại
        game_map (GameMap): bản đồ trò chơi
    Returns:
        float: giá trị heuristic
    """
    position = node.position
    diamonds_collected = node.diamonds_collected
    
    # Lấy danh sách kim cương chưa thu thập
    remaining_diamonds = []
    for diamond_pos in game_map.diamonds:
        if diamond_pos not in diamonds_collected:
            remaining_diamonds.append(diamond_pos)
    
    # Nếu đã thu thập hết kim cương, chỉ tính khoảng cách đến goal
    if not remaining_diamonds:
        return manhattan_distance(position, game_map.goal)
    
    # Tìm kim cương gần nhất
    min_distance_to_diamond = min(
        manhattan_distance(position, diamond) 
        for diamond in remaining_diamonds
    )
    
    # Tính khoảng cách từ kim cương gần nhất đến goal
    closest_diamond = min(
        remaining_diamonds,
        key=lambda d: manhattan_distance(position, d)
    )
    distance_diamond_to_goal = manhattan_distance(closest_diamond, game_map.goal)
    
    # Heuristic = khoảng cách đến kim cương gần nhất + ước tính từ kim cương đó đến goal
    # Thêm penalty cho số kim cương còn lại để khuyến khích thu thập sớm
    return min_distance_to_diamond + distance_diamond_to_goal + len(remaining_diamonds) * 2

def advanced_diamond_heuristic(node, game_map):
    """
    Hàm heuristic nâng cao sử dụng MST (Minimum Spanning Tree)
    để ước tính chi phí thu thập tất cả kim cương
    
    Args:
        node (Node): node hiện tại
        game_map (GameMap): bản đồ trò chơi
    Returns:
        float: giá trị heuristic
    """
    position = node.position
    diamonds_collected = node.diamonds_collected
    
    # Lấy danh sách kim cương chưa thu thập
    remaining_diamonds = []
    for diamond_pos in game_map.diamonds:
        if diamond_pos not in diamonds_collected:
            remaining_diamonds.append(diamond_pos)
    
    # Nếu đã thu thập hết kim cương
    if not remaining_diamonds:
        return manhattan_distance(position, game_map.goal)
    
    # Tạo danh sách tất cả điểm cần thăm (vị trí hiện tại + kim cương + goal)
    points = [position] + remaining_diamonds + [game_map.goal]
    
    # Tính ma trận khoảng cách
    n = len(points)
    distances = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dist = manhattan_distance(points[i], points[j])
            distances[i][j] = distances[j][i] = dist
    
    # Ước tính bằng cách tìm đường đi ngắn nhất từ vị trí hiện tại
    # đến kim cương gần nhất + tổng khoảng cách tối thiểu giữa các kim cương
    if len(remaining_diamonds) == 1:
        return (manhattan_distance(position, remaining_diamonds[0]) + 
                manhattan_distance(remaining_diamonds[0], game_map.goal))
    
    # Tính MST cho các kim cương còn lại
    mst_cost = 0
    visited = set()
    min_heap = [(manhattan_distance(position, remaining_diamonds[0]), 0)]  # (cost, diamond_index)
    
    while min_heap and len(visited) < len(remaining_diamonds):
        cost, diamond_idx = min(min_heap, key=lambda x: x[0])
        min_heap.remove((cost, diamond_idx))
        
        if diamond_idx in visited:
            continue
            
        visited.add(diamond_idx)
        mst_cost += cost
        
        # Thêm các cạnh từ kim cương này đến các kim cương chưa thăm
        for i, diamond in enumerate(remaining_diamonds):
            if i not in visited:
                edge_cost = manhattan_distance(remaining_diamonds[diamond_idx], diamond)
                min_heap.append((edge_cost, i))
    
    # Thêm khoảng cách từ kim cương cuối cùng đến goal
    if remaining_diamonds:
        min_distance_to_goal = min(
            manhattan_distance(diamond, game_map.goal)
            for diamond in remaining_diamonds
        )
        mst_cost += min_distance_to_goal
    
    return mst_cost