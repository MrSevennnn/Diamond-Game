# utils.py - Các hàm tiện ích và hiển thị trực quan

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np

def visualize_map_matplotlib(game_map, path=None, title="Diamond Game Map"):
    """
    Hiển thị bản đồ và đường đi bằng matplotlib
    Args:
        game_map (GameMap): bản đồ trò chơi
        path (list): đường đi cần hiển thị
        title (str): tiêu đề biểu đồ
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np
    except ImportError:
        print("Không thể import matplotlib. Vui lòng cài đặt: pip install matplotlib")
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Tạo ma trận màu để hiển thị
    rows, cols = game_map.rows, game_map.cols
    color_map = np.zeros((rows, cols))
    
    # Gán màu cho các ô
    for i in range(rows):
        for j in range(cols):
            if game_map.grid[i][j] == '#':
                color_map[i][j] = 1  # Tường - đen
            else:
                color_map[i][j] = 0  # Ô trống - trắng
    
    # Hiển thị bản đồ cơ bản
    colors = ['white', 'black', 'lightblue', 'red', 'green', 'gold', 'purple']
    cmap = ListedColormap(colors)
    ax.imshow(color_map, cmap=cmap, alpha=0.7)
    
    # Đánh dấu điểm đặc biệt
    # Start
    if game_map.start:
        start_circle = patches.Circle(
            (game_map.start[1], game_map.start[0]), 0.4, 
            color='green', alpha=0.8, linewidth=2, edgecolor='darkgreen'
        )
        ax.add_patch(start_circle)
        ax.text(game_map.start[1], game_map.start[0], 'S', 
               ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Goal
    if game_map.goal:
        goal_circle = patches.Circle(
            (game_map.goal[1], game_map.goal[0]), 0.4,
            color='red', alpha=0.8, linewidth=2, edgecolor='darkred'
        )
        ax.add_patch(goal_circle)
        ax.text(game_map.goal[1], game_map.goal[0], 'G',
               ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Diamonds
    for diamond in game_map.diamonds:
        diamond_shape = patches.RegularPolygon(
            (diamond[1], diamond[0]), 4, radius=0.3,
            color='cyan', alpha=0.8, linewidth=2, edgecolor='blue'
        )
        ax.add_patch(diamond_shape)
        ax.text(diamond[1], diamond[0], 'D',
               ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Hiển thị đường đi
    if path and len(path) > 1:
        path_x = [pos[1] for pos in path]
        path_y = [pos[0] for pos in path]
        
        # Vẽ đường đi
        ax.plot(path_x, path_y, 'o-', color='orange', linewidth=3, 
               markersize=8, alpha=0.8, label=f'Đường đi ({len(path)} bước)')
        
        # Đánh số thứ tự các bước
        for i, (x, y) in enumerate(zip(path_x, path_y)):
            if i > 0 and i < len(path) - 1:  # Không hiển thị số ở start và goal
                ax.text(x + 0.2, y + 0.2, str(i), 
                       fontsize=8, color='purple', fontweight='bold')
    
    # Cài đặt hiển thị
    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(-0.5, rows - 0.5)
    ax.set_aspect('equal')
    ax.invert_yaxis()  # Đảo ngược trục y để khớp với ma trận
    
    # Grid và labels
    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.grid(True, alpha=0.3)
    
    # Tiêu đề và chú thích
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        patches.Patch(color='green', label='Start (S)'),
        patches.Patch(color='red', label='Goal (G)'),
        patches.Patch(color='cyan', label='Diamond (D)'),
        patches.Patch(color='black', label='Wall (#)'),
        patches.Patch(color='white', label='Empty (.)'),
    ]
    
    if path:
        legend_elements.append(patches.Patch(color='orange', label='Path'))
    
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    plt.show()

def save_result_to_file(results, filename="diamond_game_results.txt"):
    """
    Lưu kết quả so sánh các thuật toán ra file
    Args:
        results (dict): kết quả từ compare_algorithms
        filename (str): tên file để lưu
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("KẾT QUẢ SO SÁNH CÁC THUẬT TOÁN TÌM KIẾM\n")
            f.write("TRÒ CHƠI KIM CƯƠNG (DIAMOND GAME)\n")
            f.write("="*60 + "\n\n")
            
            # Bảng so sánh
            f.write(f"{'Thuật toán':<15} {'Tìm thấy':<10} {'Bước':<8} {'Chi phí':<10} {'Node duyệt':<12} {'Thời gian(s)':<12}\n")
            f.write("-" * 80 + "\n")
            
            for name, result in results.items():
                if result.found_solution:
                    found = "CÓ"
                    steps = len(result.path)
                    cost = result.cost
                else:
                    found = "KHÔNG"
                    steps = "-"
                    cost = "-"
                
                f.write(f"{name:<15} {found:<10} {steps:<8} {cost:<10} {result.nodes_explored:<12} {result.execution_time:<12.4f}\n")
            
            f.write("\n" + "="*60 + "\n\n")
            
            # Chi tiết từng thuật toán
            f.write("CHI TIẾT KẾT QUẢ TỪNG THUẬT TOÁN:\n")
            f.write("="*60 + "\n")
            
            for name, result in results.items():
                f.write(str(result) + "\n")
                
                if result.found_solution and result.path:
                    f.write(f"Đường đi chi tiết:\n")
                    for i, pos in enumerate(result.path):
                        f.write(f"  Bước {i+1}: {pos}\n")
                    f.write("\n")
                
                f.write("-" * 40 + "\n\n")
        
        print(f"✓ Đã lưu kết quả vào file: {filename}")
        
    except Exception as e:
        print(f"✗ Lỗi lưu file: {e}")

def create_animated_path(game_map, path, filename="diamond_game_animation.gif"):
    """
    Tạo animation hiển thị đường đi từng bước
    Args:
        game_map (GameMap): bản đồ trò chơi
        path (list): đường đi
        filename (str): tên file gif đầu ra
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
    except ImportError:
        print("Không thể tạo animation. Vui lòng cài đặt matplotlib")
        return
    
    if not path:
        print("Không có đường đi để tạo animation")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def animate_step(frame):
        ax.clear()
        
        # Vẽ bản đồ cơ bản
        rows, cols = game_map.rows, game_map.cols
        color_map = np.zeros((rows, cols))
        
        for i in range(rows):
            for j in range(cols):
                if game_map.grid[i][j] == '#':
                    color_map[i][j] = 1
                else:
                    color_map[i][j] = 0
        
        ax.imshow(color_map, cmap='gray', alpha=0.7)
        
        # Vẽ các điểm cố định
        # Start
        start_circle = patches.Circle(
            (game_map.start[1], game_map.start[0]), 0.4, 
            color='green', alpha=0.8
        )
        ax.add_patch(start_circle)
        ax.text(game_map.start[1], game_map.start[0], 'S', 
               ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Goal
        goal_circle = patches.Circle(
            (game_map.goal[1], game_map.goal[0]), 0.4,
            color='red', alpha=0.8
        )
        ax.add_patch(goal_circle)
        ax.text(game_map.goal[1], game_map.goal[0], 'G',
               ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Diamonds
        for diamond in game_map.diamonds:
            diamond_shape = patches.RegularPolygon(
                (diamond[1], diamond[0]), 4, radius=0.3,
                color='cyan', alpha=0.8
            )
            ax.add_patch(diamond_shape)
            ax.text(diamond[1], diamond[0], 'D',
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Vẽ đường đi đã đi qua
        if frame > 0:
            past_path_x = [path[i][1] for i in range(min(frame + 1, len(path)))]
            past_path_y = [path[i][0] for i in range(min(frame + 1, len(path)))]
            ax.plot(past_path_x, past_path_y, 'o-', color='orange', 
                   linewidth=2, markersize=6, alpha=0.6)
        
        # Vẽ vị trí hiện tại
        if frame < len(path):
            current_pos = path[frame]
            current_circle = patches.Circle(
                (current_pos[1], current_pos[0]), 0.3,
                color='yellow', alpha=1, linewidth=3, edgecolor='orange'
            )
            ax.add_patch(current_circle)
        
        # Cài đặt hiển thị
        ax.set_xlim(-0.5, cols - 0.5)
        ax.set_ylim(-0.5, rows - 0.5)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.set_title(f'Diamond Game Animation - Bước {frame + 1}/{len(path)}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Tạo animation
    anim = animation.FuncAnimation(
        fig, animate_step, frames=len(path), 
        interval=800, repeat=True
    )
    
    # Lưu animation
    try:
        anim.save(filename, writer='pillow', fps=1.5)
        print(f"✓ Đã tạo animation: {filename}")
    except Exception as e:
        print(f"✗ Lỗi tạo animation: {e}")
        plt.show()  # Hiển thị trực tiếp nếu không lưu được

def print_statistics(results):
    """
    In thống kê chi tiết về kết quả các thuật toán
    Args:
        results (dict): kết quả từ compare_algorithms
    """
    print("\n" + "="*60)
    print("THỐNG KÊ CHI TIẾT")
    print("="*60)
    
    successful_results = {name: result for name, result in results.items() if result.found_solution}
    
    if not successful_results:
        print("Không có thuật toán nào tìm thấy lời giải!")
        return
    
    # Thống kê tổng quan
    total_algorithms = len(results)
    successful_count = len(successful_results)
    
    print(f"📊 Tổng số thuật toán: {total_algorithms}")
    print(f"Số thuật toán thành công: {successful_count}")
    print(f"Số thuật toán thất bại: {total_algorithms - successful_count}")
    print(f"Tỷ lệ thành công: {successful_count/total_algorithms*100:.1f}%")
    
    if successful_results:
        # Phân tích chi phí
        costs = [result.cost for result in successful_results.values()]
        print(f"\n💰 PHÂN TÍCH CHI PHÍ:")
        print(f"• Chi phí thấp nhất: {min(costs)}")
        print(f"• Chi phí cao nhất: {max(costs)}")
        print(f"• Chi phí trung bình: {sum(costs)/len(costs):.2f}")
        
        # Phân tích thời gian
        times = [result.execution_time for result in successful_results.values()]
        print(f"\nPHÂN TÍCH THỜI GIAN:")
        print(f"• Thời gian nhanh nhất: {min(times):.4f}s")
        print(f"• Thời gian chậm nhất: {max(times):.4f}s")
        print(f"• Thời gian trung bình: {sum(times)/len(times):.4f}s")
        
        # Phân tích số node
        nodes = [result.nodes_explored for result in successful_results.values()]
        print(f"\nPHÂN TÍCH SỐ NODE DUYỆT:")
        print(f"• Ít nhất: {min(nodes)} nodes")
        print(f"• Nhiều nhất: {max(nodes)} nodes") 
        print(f"• Trung bình: {sum(nodes)/len(nodes):.2f} nodes")
        
        # Hiệu quả tổng thể (kết hợp nhiều yếu tố)
        print(f"\nXẾP HẠNG HIỆU QUẢ TỔNG THỂ:")
        
        # Tính điểm hiệu quả (lower is better)
        efficiency_scores = {}
        for name, result in successful_results.items():
            # Normalize các metrics (0-1)
            cost_score = (result.cost - min(costs)) / (max(costs) - min(costs)) if max(costs) > min(costs) else 0
            time_score = (result.execution_time - min(times)) / (max(times) - min(times)) if max(times) > min(times) else 0
            nodes_score = (result.nodes_explored - min(nodes)) / (max(nodes) - min(nodes)) if max(nodes) > min(nodes) else 0
            
            # Tổng điểm (weight: cost=40%, time=30%, nodes=30%)
            total_score = cost_score * 0.4 + time_score * 0.3 + nodes_score * 0.3
            efficiency_scores[name] = total_score
        
        # Sắp xếp theo điểm hiệu quả
        ranked_algorithms = sorted(efficiency_scores.items(), key=lambda x: x[1])
        
        for i, (name, score) in enumerate(ranked_algorithms, 1):
            result = successful_results[name]
            print(f"{i}. {name}: "
                 f"Chi phí={result.cost}, "
                 f"Thời gian={result.execution_time:.4f}s, "
                 f"Nodes={result.nodes_explored} "
                 f"(Điểm: {score:.3f})")

if __name__ == "__main__":
    print("Module utils.py - Các hàm tiện ích cho trò chơi Kim cương")
    print("Sử dụng các hàm này từ module khác để hiển thị trực quan và phân tích kết quả.")