import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data.sqlite_db import init_database, save_prayers_to_db

TEXT_PATH = Path(__file__).resolve().parents[2] / "khan.txt"


def extract_catalog_from_txt(text: str) -> List[Dict[str, Any]]:
    """Trích xuất mục lục từ file txt"""
    catalog = []
    lines = text.split('\n')
    
    # Pattern để tìm các mục có số thứ tự: "1. Văn cúng..."
    pattern = re.compile(r'^(\d+)\.\s*(Văn cúng.+)$')
    
    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            number = int(match.group(1))
            title = match.group(2).strip()
            # Bỏ phần số trang nếu có (dấu … hoặc ...)
            title = re.sub(r'\s*[…\.]+\s*\d+$', '', title)
            catalog.append({
                'id': f'bai_{number:03d}',
                'number': number,
                'title': title
            })
    
    return catalog


def extract_content_for_prayers(text: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trích xuất nội dung cho từng bài văn cúng"""
    prayers = []
    
    for i, item in enumerate(catalog):
        title = item['title']
        number = item['number']
        
        # Tìm vị trí bắt đầu của bài trong text
        # Tìm dòng có "X. Văn cúng..."
        start_pattern = re.compile(rf'^{number}\.\s*{re.escape(title)}', re.MULTILINE)
        start_match = start_pattern.search(text)
        
        if start_match:
            start_pos = start_match.start()
            
            # Tìm vị trí kết thúc (bài tiếp theo hoặc === separator)
            end_pos = len(text)
            if i + 1 < len(catalog):
                next_title = catalog[i + 1]['title']
                next_number = catalog[i + 1]['number']
                next_pattern = re.compile(rf'^{next_number}\.\s*{re.escape(next_title)}', re.MULTILINE)
                next_match = next_pattern.search(text)
                if next_match:
                    end_pos = next_match.start()
            
            # Lấy nội dung
            content = text[start_pos:end_pos].strip()
            
            # Làm sạch nội dung
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # Thay thế placeholder bằng template variables
            content = content.replace('…', '{ten_be}')  # Dấu … thường là chỗ điền tên
            content = content.replace('...', '{ten_be}')  # Hoặc ...
            
            prayers.append({
                'id': item['id'],
                'title': item['title'],
                'template': content
            })
            print(f'  ✓ [{number:2d}] {title[:50]}...')
        else:
            prayers.append({
                'id': item['id'],
                'title': item['title'],
                'template': f'Nội dung cho {title}'
            })
            print(f'  - [{number:2d}] {title[:50]}... (placeholder)')
    
    return prayers


def create_catalog_from_txt() -> None:
    """Tạo database từ file khan.txt"""
    print("Đang tạo database từ file khan.txt")
    print("=" * 60)
    
    if not TEXT_PATH.exists():
        print(f"Không tìm thấy file: {TEXT_PATH}")
        return
    
    # Khởi tạo database
    init_database()
    
    try:
        # Đọc file
        print("1. Đọc file khan.txt...")
        text = TEXT_PATH.read_text(encoding='utf-8')
        print(f"   Đã đọc {len(text)} ký tự")
        
        # Trích xuất mục lục
        print("\n2. Trích xuất mục lục:")
        catalog = extract_catalog_from_txt(text)
        print(f"   Tìm thấy {len(catalog)} bài")
        
        # Trích xuất nội dung
        print("\n3. Trích xuất nội dung:")
        prayers = extract_content_for_prayers(text, catalog)
        
        # Lưu vào database
        print(f"\n4. Lưu vào database...")
        save_prayers_to_db(prayers)
        
        print(f"\n" + "=" * 60)
        print(f"HOÀN THÀNH! Đã tạo database với {len(prayers)} bài")
        print("=" * 60)
        
        # Hiển thị danh sách
        print("\nDanh sách các bài:")
        for i, prayer in enumerate(prayers, 1):
            print(f'{i:2d}. {prayer["id"]} - {prayer["title"]}')
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_catalog_from_txt()
