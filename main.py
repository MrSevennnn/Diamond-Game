# main.py - Chương trình chính trò chơi Kim cương
"""
Trò chơi Kim cương (Diamond Game) - Ứng dụng AI tìm kiếm đường đi

Cách sử dụng:
- Chạy giao diện đồ họa (mặc định): python main.py  
- Chạy giao diện dòng lệnh: python main.py --console

Tác giả: Sinh viên thực tập Trí tuệ nhân tạo
Ngày: October 2025
"""

import os
import sys
import argparse
from game import GameMap
from search import (bfs, dfs, ucs, greedy_best_first, a_star, compare_algorithms)
from heuristic import diamond_heuristic

def visualize_solution(game_map, result):
    """
    Hiển thị lời giải trực quan
    Args:
        game_map (GameMap): bản đồ trò chơi
        result (SearchResult): kết quả tìm kiếm
    """
    if not result.found_solution:
        print("Không tìm thấy lời giải để hiển thị!")
        return
    
    print(f"\n--- HIỂN THỊ ĐƯỜNG ĐI THUẬT TOÁN {result.algorithm.upper()} ---")
    
    # Hiển thị bản đồ với đường đi
    game_map.display_map(path=result.path)
    
    # Hiển thị từng bước di chuyển
    print(f"\nCác bước di chuyển ({len(result.path)} bước):")
    diamonds_found = []
    
    for i, pos in enumerate(result.path):
        step_info = f"Bước {i+1}: {pos}"
        
        # Kiểm tra thu thập kim cương
        if pos in game_map.diamonds:
            diamonds_found.append(pos)
            step_info += " (Thu thập kim cương)"
        elif pos == game_map.start:
            step_info += " (Điểm bắt đầu)"
        elif pos == game_map.goal:
            step_info += " (Điểm đích)"
        
        print(step_info)
    
    print(f"\nTổng kim cương thu thập được: {len(diamonds_found)}/{len(game_map.diamonds)}")
    if diamonds_found:
        print(f"Vị trí kim cương: {diamonds_found}")

def run_single_algorithm(game_map, algorithm_name):
    """
    Chạy một thuật toán cụ thể
    Args:
        game_map (GameMap): bản đồ trò chơi  
        algorithm_name (str): tên thuật toán
    """
    algorithms = {
        'bfs': bfs,
        'dfs': dfs, 
        'ucs': ucs,
        'greedy': greedy_best_first,
        'astar': a_star
    }
    
    if algorithm_name not in algorithms:
        print(f"Thuật toán '{algorithm_name}' không được hỗ trợ!")
        return None
    
    print(f"\nChạy thuật toán {algorithm_name.upper()}...")
    try:
        result = algorithms[algorithm_name](game_map)
        print(result)
        
        if result.found_solution:
            show_visual = input("\nBạn có muốn xem đường đi trực quan? (y/n): ").lower().strip()
            if show_visual in ['y', 'yes', '1']:
                visualize_solution(game_map, result)
                
                # Hiển thị trực quan với matplotlib nếu có
                try:
                    show_matplotlib = input("Hiển thị bằng đồ họa matplotlib? (y/n): ").lower().strip()
                    if show_matplotlib in ['y', 'yes', '1']:
                        from utils import visualize_map_matplotlib
                        visualize_map_matplotlib(
                            game_map, 
                            path=result.path, 
                            title=f"Kết quả {result.algorithm} - Chi phí: {result.cost}"
                        )
                except ImportError:
                    print("Cài đặt matplotlib để xem đồ họa: pip install matplotlib")
                except Exception as e:
                    print(f"Lỗi hiển thị đồ họa: {e}")
        
        return result
        
    except Exception as e:
        print(f"Lỗi khi chạy thuật toán: {e}")
        return None

def display_comparison_table(results):
    """
    Hiển thị bảng so sánh kết quả các thuật toán
    Args:
        results (dict): kết quả từ compare_algorithms
    """
    print("\n" + "="*100)
    print("📊 BẢNG SO SÁNH KẾT QUẢ CÁC THUẬT TOÁN")
    print("="*100)
    
    # Header
    header = f"{'Thuật toán':<15} {'Tìm thấy':<10} {'Bước':<8} {'Chi phí':<10} {'Node duyệt':<12} {'Thời gian(s)':<12}"
    print(header)
    print("-" * 100)
    
    # Dữ liệu cho mỗi thuật toán
    for name, result in results.items():
        if result.found_solution:
            found = "✓"
            steps = len(result.path)
            cost = result.cost
        else:
            found = "✗" 
            steps = "-"
            cost = "-"
        
        row = f"{name:<15} {found:<10} {steps:<8} {cost:<10} {result.nodes_explored:<12} {result.execution_time:<12.4f}"
        print(row)
    
    print("="*100)
    
    # Tìm thuật toán tốt nhất
    successful_results = {name: result for name, result in results.items() if result.found_solution}
    
    if successful_results:
        print("\nTHUẬT TOÁN TỐT NHẤT:")
        
        # Tốt nhất theo chi phí
        best_cost = min(successful_results.values(), key=lambda x: x.cost)
        print(f"• Chi phí thấp nhất: {best_cost.algorithm} (Chi phí: {best_cost.cost})")
        
        # Tốt nhất theo thời gian
        best_time = min(successful_results.values(), key=lambda x: x.execution_time)
        print(f"• Thời gian nhanh nhất: {best_time.algorithm} ({best_time.execution_time:.4f}s)")
        
        # Tốt nhất theo số node
        best_nodes = min(successful_results.values(), key=lambda x: x.nodes_explored)
        print(f"• Ít node duyệt nhất: {best_nodes.algorithm} ({best_nodes.nodes_explored} nodes)")
    
    # Import và sử dụng hàm thống kê từ utils
    try:
        from utils import print_statistics
        print_statistics(results)
    except ImportError:
        pass

def show_usage_guide():
    """Hiển thị hướng dẫn sử dụng"""
    print("\n" + "="*70)
    print("HƯỚNG DẪN SỬ DỤNG TRÒ CHƠI KIM CƯƠNG")
    print("="*70)
    
    print("""
MỤC TIÊU:
Thu thập tất cả kim cương (D) và đến được vị trí đích (G) với chi phí tối thiểu.

KÝ HIỆU BẢNG ĐỒ:
• S: Điểm bắt đầu (Start)
• D: Kim cương (Diamond)  
• G: Điểm đích (Goal)
• #: Tường/Chướng ngại vật
• .: Ô trống có thể di chuyển
• *: Đường đi (khi hiển thị kết quả)

CÁC THUẬT TOÁN:
• BFS: Tìm kiếm theo chiều rộng - đảm bảo tối ưu
• DFS: Tìm kiếm theo chiều sâu - tiết kiệm bộ nhớ
• UCS: Chi phí đồng nhất - tối ưu về chi phí  
• Greedy: Tham lam - nhanh nhưng không đảm bảo tối ưu
• A*: Kết hợp g(n) + h(n) - cân bằng tốc độ và tối ưu

CÁCH SỬ DỤNG:
1. Chọn thuật toán từ menu
2. Xem kết quả: đường đi, chi phí, số node duyệt
3. So sánh tất cả thuật toán
4. Thay đổi bản đồ để thử nghiệm khác nhau

HIỂN THỊ KẾT QUẢ:
• Đường đi: Danh sách vị trí từ S đến G
• Chi phí: Tổng số bước di chuyển
• Node duyệt: Số trạng thái đã khám phá
• Thời gian: Thời gian thực thi thuật toán

TÍNH NĂNG NÂNG CAO:
• Hiển thị trực quan với Matplotlib (menu 11)
• Lưu kết quả ra file (menu 12) 
• Tạo bản đồ mẫu với độ khó khác nhau
• Animation đường đi (nếu có matplotlib)

YÊU CẦU:
• Python 3.7+
• Matplotlib (tùy chọn, cho hiển thị đồ họa)

MẸO SỬ DỤNG:
• Thử các bản đồ khác nhau để thấy sự khác biệt giữa thuật toán
• So sánh các thuật toán để thấy hiệu suất khác nhau
• Dùng bản đồ lớn để thấy rõ hiệu suất các thuật toán
    """)
    
    print("="*70)

def main_console():
    """Chạy giao diện dòng lệnh đơn giản - so sánh tất cả thuật toán"""
    print("CHÀO MỪNG ĐẾN VỚI TRÒ CHƠI KIM CƯƠNG!")
    
    # Tải bản đồ mặc định
    try:
        map_file = 'map_simple.txt'  # Sử dụng bản đồ đơn giản
        game_map = GameMap(map_file)
        print(f"\nĐã tải bản đồ từ: {map_file}")
        
    except Exception as e:
        print(f"\nLỗi tải bản đồ: {e}")
        return
    
    # Hiển thị bản đồ
    print("\n--- BẢN ĐỒ HIỆN TẠI ---")
    game_map.display_map()
    
    # Hiển thị thông tin bản đồ
    info = game_map.get_map_info()
    print(f"\n--- THÔNG TIN BẢN ĐỒ ---")
    print(f"Kích thước: {info['rows']} x {info['cols']}")
    print(f"Điểm bắt đầu: {info['start']}")
    print(f"Điểm đích: {info['goal']}")
    print(f"Số kim cương: {info['diamonds_count']}")
    print(f"Vị trí kim cương: {info['diamonds_positions']}")
    
    # Chạy so sánh tất cả thuật toán
    print("\n--- CHẠY SO SÁNH TẤT CẢ THUẬT TOÁN ---")
    results = compare_algorithms(game_map)
    display_comparison_table(results)
    
    print("\nHoàn thành! Sử dụng giao diện đồ họa để tương tác chi tiết hơn.")
    print("Chạy lệnh: python main.py (không có --console)")

def main():
    """Hàm chính - mặc định chạy giao diện đồ họa"""
    parser = argparse.ArgumentParser(description='Trò chơi Kim cương - Diamond Game')
    parser.add_argument('--console', '-c', action='store_true', 
                       help='Chạy giao diện dòng lệnh thay vì giao diện đồ họa')
    
    args = parser.parse_args()
    
    if args.console:
        # Chạy giao diện dòng lệnh khi có tham số --console
        print("Khởi động giao diện dòng lệnh...")
        main_console()
    else:
        # Mặc định chạy giao diện đồ họa
        try:
            print("Khởi động trò chơi Kim cương...")
            print("Sử dụng 'python main.py --console' để chạy giao diện dòng lệnh")
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Lỗi import giao diện đồ họa: {e}")
            print("Đảm bảo tất cả các file cần thiết có mặt trong thư mục")
            print("Chuyển sang giao diện dòng lệnh...")
            main_console()
        except Exception as e:
            print(f"Lỗi khởi động giao diện đồ họa: {e}")
            print("Chuyển sang giao diện dòng lệnh...")
            main_console()

if __name__ == "__main__":
    main()