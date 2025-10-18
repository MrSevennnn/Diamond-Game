# search.py - Các thuật toán tìm kiếm cho trò chơi Kim cương

import time
from collections import deque
import heapq
from node import Node
from heuristic import diamond_heuristic

class SearchResult:
    """
    Lớp lưu trữ kết quả tìm kiếm
    """
    def __init__(self, path=None, cost=0, nodes_explored=0, execution_time=0, algorithm=""):
        self.path = path or []
        self.cost = cost
        self.nodes_explored = nodes_explored
        self.execution_time = execution_time
        self.algorithm = algorithm
        self.found_solution = len(self.path) > 0
    
    def __str__(self):
        if self.found_solution:
            return (f"\n=== KẾT QUẢ THUẬT TOÁN {self.algorithm.upper()} ===\n"
                   f"Tìm thấy lời giải: CÓ\n"
                   f"Độ dài đường đi: {len(self.path)} bước\n"
                   f"Chi phí: {self.cost}\n"
                   f"Số node đã duyệt: {self.nodes_explored}\n"
                   f"Thời gian thực thi: {self.execution_time:.4f} giây\n"
                   f"Đường đi: {' -> '.join(map(str, self.path))}\n")
        else:
            return (f"\n=== KẾT QUẢ THUẬT TOÁN {self.algorithm.upper()} ===\n"
                   f"Tìm thấy lời giải: KHÔNG\n"
                   f"Số node đã duyệt: {self.nodes_explored}\n"
                   f"Thời gian thực thi: {self.execution_time:.4f} giây\n")

def bfs(game_map):
    """
    Thuật toán tìm kiếm theo chiều rộng (BFS)
    Args:
        game_map (GameMap): bản đồ trò chơi
    Returns:
        SearchResult: kết quả tìm kiếm
    """
    start_time = time.time()
    
    start_node = Node(
        position=game_map.start,
        diamonds_collected=frozenset(),
        g_cost=0
    )
    
    if game_map.is_goal_state(start_node.position, start_node.diamonds_collected):
        return SearchResult([start_node.position], 0, 1, time.time() - start_time, "BFS")
    
    queue = deque([start_node])
    visited = {(start_node.position, start_node.diamonds_collected)}
    nodes_explored = 0
    
    while queue:
        current_node = queue.popleft()
        nodes_explored += 1
        
        # Duyệt các node láng giềng
        for neighbor_pos in game_map.get_neighbors(current_node.position):
            # Thu thập kim cương tại vị trí mới (nếu có)
            new_diamonds = game_map.collect_diamond(neighbor_pos, current_node.diamonds_collected)
            
            state_key = (neighbor_pos, new_diamonds)
            if state_key not in visited:
                visited.add(state_key)
                
                neighbor_node = Node(
                    position=neighbor_pos,
                    diamonds_collected=new_diamonds,
                    g_cost=current_node.g_cost + 1,
                    parent=current_node
                )
                
                # Kiểm tra đích
                if game_map.is_goal_state(neighbor_node.position, neighbor_node.diamonds_collected):
                    path = neighbor_node.get_path()
                    return SearchResult(
                        path, 
                        neighbor_node.g_cost, 
                        nodes_explored, 
                        time.time() - start_time, 
                        "BFS"
                    )
                
                queue.append(neighbor_node)
    
    return SearchResult([], 0, nodes_explored, time.time() - start_time, "BFS")

def dfs(game_map, max_depth=1000):
    """
    Thuật toán tìm kiếm theo chiều sâu (DFS)
    Args:
        game_map (GameMap): bản đồ trò chơi
        max_depth (int): độ sâu tối đa
    Returns:
        SearchResult: kết quả tìm kiếm
    """
    start_time = time.time()
    
    start_node = Node(
        position=game_map.start,
        diamonds_collected=frozenset(),
        g_cost=0
    )
    
    if game_map.is_goal_state(start_node.position, start_node.diamonds_collected):
        return SearchResult([start_node.position], 0, 1, time.time() - start_time, "DFS")
    
    stack = [start_node]
    visited = {(start_node.position, start_node.diamonds_collected)}
    nodes_explored = 0
    
    while stack:
        current_node = stack.pop()
        nodes_explored += 1
        
        # Kiểm tra độ sâu tối đa
        if current_node.g_cost >= max_depth:
            continue
        
        # Duyệt các node láng giềng
        for neighbor_pos in game_map.get_neighbors(current_node.position):
            # Thu thập kim cương tại vị trí mới (nếu có)
            new_diamonds = game_map.collect_diamond(neighbor_pos, current_node.diamonds_collected)
            
            state_key = (neighbor_pos, new_diamonds)
            if state_key not in visited:
                visited.add(state_key)
                
                neighbor_node = Node(
                    position=neighbor_pos,
                    diamonds_collected=new_diamonds,
                    g_cost=current_node.g_cost + 1,
                    parent=current_node
                )
                
                # Kiểm tra đích
                if game_map.is_goal_state(neighbor_node.position, neighbor_node.diamonds_collected):
                    path = neighbor_node.get_path()
                    return SearchResult(
                        path, 
                        neighbor_node.g_cost, 
                        nodes_explored, 
                        time.time() - start_time, 
                        "DFS"
                    )
                
                stack.append(neighbor_node)
    
    return SearchResult([], 0, nodes_explored, time.time() - start_time, "DFS")

def ucs(game_map):
    """
    Thuật toán tìm kiếm chi phí đồng nhất (UCS)
    Args:
        game_map (GameMap): bản đồ trò chơi
    Returns:
        SearchResult: kết quả tìm kiếm
    """
    start_time = time.time()
    
    start_node = Node(
        position=game_map.start,
        diamonds_collected=frozenset(),
        g_cost=0
    )
    
    if game_map.is_goal_state(start_node.position, start_node.diamonds_collected):
        return SearchResult([start_node.position], 0, 1, time.time() - start_time, "UCS")
    
    # Priority queue: (g_cost, node)
    priority_queue = [(0, id(start_node), start_node)]
    visited = {}
    nodes_explored = 0
    
    while priority_queue:
        current_cost, _, current_node = heapq.heappop(priority_queue)
        nodes_explored += 1
        
        state_key = (current_node.position, current_node.diamonds_collected)
        
        # Skip nếu đã thăm với chi phí tốt hơn
        if state_key in visited and visited[state_key] <= current_cost:
            continue
        
        visited[state_key] = current_cost
        
        # Kiểm tra đích
        if game_map.is_goal_state(current_node.position, current_node.diamonds_collected):
            path = current_node.get_path()
            return SearchResult(
                path, 
                current_node.g_cost, 
                nodes_explored, 
                time.time() - start_time, 
                "UCS"
            )
        
        # Duyệt các node láng giềng
        for neighbor_pos in game_map.get_neighbors(current_node.position):
            # Thu thập kim cương tại vị trí mới (nếu có)
            new_diamonds = game_map.collect_diamond(neighbor_pos, current_node.diamonds_collected)
            new_cost = current_node.g_cost + 1
            
            neighbor_state = (neighbor_pos, new_diamonds)
            
            # Thêm vào queue nếu chưa thăm hoặc có chi phí tốt hơn
            if neighbor_state not in visited or visited[neighbor_state] > new_cost:
                neighbor_node = Node(
                    position=neighbor_pos,
                    diamonds_collected=new_diamonds,
                    g_cost=new_cost,
                    parent=current_node
                )
                
                heapq.heappush(priority_queue, (new_cost, id(neighbor_node), neighbor_node))
    
    return SearchResult([], 0, nodes_explored, time.time() - start_time, "UCS")

def greedy_best_first(game_map, heuristic_func=diamond_heuristic):
    """
    Thuật toán tìm kiếm tham lam tốt nhất (Greedy Best-First)
    Args:
        game_map (GameMap): bản đồ trò chơi
        heuristic_func: hàm heuristic
    Returns:
        SearchResult: kết quả tìm kiếm
    """
    start_time = time.time()
    
    start_node = Node(
        position=game_map.start,
        diamonds_collected=frozenset(),
        g_cost=0,
        h_cost=heuristic_func(Node(game_map.start, frozenset()), game_map)
    )
    
    if game_map.is_goal_state(start_node.position, start_node.diamonds_collected):
        return SearchResult([start_node.position], 0, 1, time.time() - start_time, "Greedy")
    
    # Priority queue: (h_cost, node)
    priority_queue = [(start_node.h_cost, id(start_node), start_node)]
    visited = set()
    nodes_explored = 0
    
    while priority_queue:
        _, _, current_node = heapq.heappop(priority_queue)
        nodes_explored += 1
        
        state_key = (current_node.position, current_node.diamonds_collected)
        
        if state_key in visited:
            continue
        
        visited.add(state_key)
        
        # Kiểm tra đích
        if game_map.is_goal_state(current_node.position, current_node.diamonds_collected):
            path = current_node.get_path()
            return SearchResult(
                path, 
                current_node.g_cost, 
                nodes_explored, 
                time.time() - start_time, 
                "Greedy"
            )
        
        # Duyệt các node láng giềng
        for neighbor_pos in game_map.get_neighbors(current_node.position):
            # Thu thập kim cương tại vị trí mới (nếu có)
            new_diamonds = game_map.collect_diamond(neighbor_pos, current_node.diamonds_collected)
            
            neighbor_state = (neighbor_pos, new_diamonds)
            
            if neighbor_state not in visited:
                neighbor_node = Node(
                    position=neighbor_pos,
                    diamonds_collected=new_diamonds,
                    g_cost=current_node.g_cost + 1,
                    h_cost=heuristic_func(Node(neighbor_pos, new_diamonds), game_map),
                    parent=current_node
                )
                
                heapq.heappush(priority_queue, (neighbor_node.h_cost, id(neighbor_node), neighbor_node))
    
    return SearchResult([], 0, nodes_explored, time.time() - start_time, "Greedy")

def a_star(game_map, heuristic_func=diamond_heuristic):
    """
    Thuật toán A*
    Args:
        game_map (GameMap): bản đồ trò chơi
        heuristic_func: hàm heuristic
    Returns:
        SearchResult: kết quả tìm kiếm
    """
    start_time = time.time()
    
    start_node = Node(
        position=game_map.start,
        diamonds_collected=frozenset(),
        g_cost=0,
        h_cost=heuristic_func(Node(game_map.start, frozenset()), game_map)
    )
    
    if game_map.is_goal_state(start_node.position, start_node.diamonds_collected):
        return SearchResult([start_node.position], 0, 1, time.time() - start_time, "A*")
    
    # Priority queue: (f_cost, g_cost, node)
    priority_queue = [(start_node.f_cost, start_node.g_cost, id(start_node), start_node)]
    visited = {}
    nodes_explored = 0
    
    while priority_queue:
        current_f, current_g, _, current_node = heapq.heappop(priority_queue)
        nodes_explored += 1
        
        state_key = (current_node.position, current_node.diamonds_collected)
        
        # Skip nếu đã thăm với chi phí g tốt hơn
        if state_key in visited and visited[state_key] <= current_g:
            continue
        
        visited[state_key] = current_g
        
        # Kiểm tra đích
        if game_map.is_goal_state(current_node.position, current_node.diamonds_collected):
            path = current_node.get_path()
            return SearchResult(
                path, 
                current_node.g_cost, 
                nodes_explored, 
                time.time() - start_time, 
                "A*"
            )
        
        # Duyệt các node láng giềng
        for neighbor_pos in game_map.get_neighbors(current_node.position):
            # Thu thập kim cương tại vị trí mới (nếu có)
            new_diamonds = game_map.collect_diamond(neighbor_pos, current_node.diamonds_collected)
            new_g_cost = current_node.g_cost + 1
            
            neighbor_state = (neighbor_pos, new_diamonds)
            
            # Thêm vào queue nếu chưa thăm hoặc có chi phí g tốt hơn
            if neighbor_state not in visited or visited[neighbor_state] > new_g_cost:
                neighbor_node = Node(
                    position=neighbor_pos,
                    diamonds_collected=new_diamonds,
                    g_cost=new_g_cost,
                    h_cost=heuristic_func(Node(neighbor_pos, new_diamonds), game_map),
                    parent=current_node
                )
                
                heapq.heappush(priority_queue, (
                    neighbor_node.f_cost, 
                    neighbor_node.g_cost, 
                    id(neighbor_node), 
                    neighbor_node
                ))
    
    return SearchResult([], 0, nodes_explored, time.time() - start_time, "A*")

def compare_algorithms(game_map):
    """
    So sánh tất cả các thuật toán
    Args:
        game_map (GameMap): bản đồ trò chơi
    Returns:
        dict: kết quả của tất cả thuật toán
    """
    print("\n" + "="*60)
    print("BẮT ĐẦU SO SÁNH CÁC THUẬT TOÁN TÌM KIẾM")
    print("="*60)
    
    algorithms = [
        ("BFS", lambda: bfs(game_map)),
        ("DFS", lambda: dfs(game_map)),
        ("UCS", lambda: ucs(game_map)),
        ("Greedy", lambda: greedy_best_first(game_map)),
        ("A*", lambda: a_star(game_map))
    ]
    
    results = {}
    
    for name, algorithm in algorithms:
        print(f"\nChạy thuật toán {name}...")
        try:
            result = algorithm()
            results[name] = result
            print(result)
        except Exception as e:
            print(f"Lỗi khi chạy thuật toán {name}: {e}")
            results[name] = SearchResult(algorithm=name)
    
    return results