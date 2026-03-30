import sqlite3
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data.sqlite_db import init_database, save_prayers_to_db

TEXT_PATH = Path(__file__).resolve().parents[2] / "vankhan.txt"


def parse_vankhan_text(file_path: Path) -> List[Dict[str, Any]]:
    """Parse vankhan.txt để trích xuất các bài văn khấn"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    prayers = []
    lines = content.split('\n')
    
    current_prayer = {}
    current_content = []
    prayer_counter = 1
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect prayer titles
        if line.startswith('Văn khấn') or 'Văn khấn' in line:
            # Save previous prayer if exists
            if current_prayer and current_content:
                current_prayer['template'] = '\n'.join(current_content)
                prayers.append(current_prayer.copy())
            
            # Start new prayer
            title = line
            # Create unique ID using counter
            prayer_id = f"bai_{prayer_counter}"
            prayer_counter += 1
            
            current_prayer = {
                'id': prayer_id,
                'title': title,
                'template': ''
            }
            current_content = []
            i += 1
            continue
            
        # Add content
        if line:
            current_content.append(line)
            
        i += 1
    
    # Save last prayer
    if current_prayer and current_content:
        current_prayer['template'] = '\n'.join(current_content)
        prayers.append(current_prayer)
    
    return prayers


def add_template_variables(prayers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Thêm các biến template vào prayers"""
    for prayer in prayers:
        template = prayer['template']
        
        # Replace placeholders with template variables
        template = template.replace(
            'Tín chủ (chúng) con là:............................................',
            'Tín chủ (chúng) con là: {ten_be}'
        ).replace(
            'Ngụ tại:....................................................................',
            'Ngụ tại: {dia_chi}'
        ).replace(
            'Hôm nay là ngày...... tháng...... năm....,',
            'Hôm nay là {ngay_thang},'
        ).replace(
            'Hôm nay là ngày...... tháng...... năm....',
            'Hôm nay là {ngay_thang}'
        ).replace(
            'Tín chủ (chúng) con là:.............................................\'',
            'Tín chủ (chúng) con là: {ten_be}'
        ).replace(
            'Ngụ tại:......................................................................',
            'Ngụ tại: {dia_chi}'
        )
        
        prayer['template'] = template
    
    return prayers


def populate_database_from_text() -> None:
    """Điền dữ liệu vào database từ file text"""
    print("Đang khởi tạo database từ vankhan.txt...")
    
    # Khởi tạo database
    init_database()
    
    # Parse file text
    if not TEXT_PATH.exists():
        print(f"Không tìm thấy file: {TEXT_PATH}")
        return
    
    prayers = parse_vankhan_text(TEXT_PATH)
    prayers = add_template_variables(prayers)
    
    # Lưu vào database
    save_prayers_to_db(prayers)
    
    print(f"Đã lưu {len(prayers)} bài văn khấn vào database từ file text")
    
    # Hiển thị danh sách các bài
    print("\nDanh sách các bài đã lưu:")
    for i, prayer in enumerate(prayers, 1):
        print(f"{i}. {prayer['title']}")
    
    print("\nHoàn thành!")


if __name__ == "__main__":
    populate_database_from_text()
