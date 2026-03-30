import sqlite3
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data.sqlite_db import init_database, save_prayers_to_db
from pypdf import PdfReader

PDF_PATH = Path(__file__).resolve().parents[2] / "vankhan1.pdf"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Đọc toàn bộ text từ PDF"""
    reader = PdfReader(pdf_path)
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text


def extract_catalog_from_pdf(text: str) -> List[Dict[str, Any]]:
    """Trích xuất nguyên mục lục từ PDF"""
    
    # Tìm phần mục lục - thường có dạng số. + tên bài
    lines = text.split('\n')
    catalog_items = []
    
    # Pattern để tìm mục lục: số. + tên bài
    catalog_pattern = re.compile(r'^(\d+)\.\s*(.+)$')
    
    print("Đang tìm mục lục trong PDF...")
    
    for line in lines:
        line = line.strip()
        match = catalog_pattern.match(line)
        
        if match:
            number = int(match.group(1))
            title = match.group(2).strip()
            
            # Làm sạch tiêu đề
            title = re.sub(r'\s+', ' ', title)  # Thay thế nhiều khoảng trắng
            title = title.replace('\n', ' ')     # Xóa xuống dòng
            
            # Bỏ các dòng quá ngắn hoặc không phải tiêu đề
            if len(title) > 10 and len(title) < 200:
                catalog_items.append({
                    'id': f'item_{number:03d}',  # ID theo thứ tự: item_001, item_002...
                    'title': title,
                    'number': number,
                    'template': f'Nội dung cho {title}'  # Placeholder
                })
                print(f'  {number:2d}. {title}')
    
    return catalog_items


def extract_content_for_each_item(text: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trích xuất nội dung cho từng mục trong mục lục"""
    
    print(f"\nĐang trích xuất nội dung cho {len(catalog)} mục...")
    
    # Tìm vị trí của từng tiêu đề trong text
    found_items = []
    
    for item in catalog:
        title = item['title']
        # Tạo pattern để tìm tiêu đề chính xác
        escaped_title = re.escape(title)
        pattern = re.compile(f'{escaped_title}', re.IGNORECASE)
        
        match = pattern.search(text)
        if match:
            found_items.append({
                'id': item['id'],
                'title': item['title'],
                'number': item['number'],
                'start_pos': match.start()
            })
    
    # Sắp xếp theo vị trí xuất hiện
    found_items.sort(key=lambda x: x['start_pos'])
    
    # Trích xuất nội dung giữa các tiêu đề
    results = []
    for i, item in enumerate(found_items):
        start_pos = item['start_pos']
        
        # Tìm vị trí kết thúc (tiêu đề tiếp theo)
        end_pos = len(text)
        if i + 1 < len(found_items):
            end_pos = found_items[i + 1]['start_pos']
        
        # Lấy nội dung
        content = text[start_pos:end_pos].strip()
        
        # Làm sạch nội dung
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ ]{2,}', ' ', content)
        
        # Thêm template variables
        content = content.replace(
            'Tín chủ (chúng) con là:............................................',
            'Tín chủ (chúng) con là: {ten_be}'
        ).replace(
            'Ngụ tại:....................................................................',
            'Ngụ tại: {dia_chi}'
        ).replace(
            'Hôm nay là ngày...... tháng...... năm....,',
            'Hôm nay là {ngay_thang},'
        )
        
        # Chỉ giữ lại nếu có nội dung đủ dài
        if len(content) > 100:
            results.append({
                'id': item['id'],
                'title': item['title'],
                'template': content
            })
            print(f'  ✓ Đã trích xuất: {item["title"]}')
        else:
            # Dùng placeholder nếu không có nội dung
            results.append({
                'id': item['id'],
                'title': item['title'],
                'template': f'Nội dung cho {item["title"]}'
            })
            print(f'  - Placeholder: {item["title"]}')
    
    return results


def create_complete_catalog() -> None:
    """Tạo database với nguyên mục lục từ PDF"""
    print("Đang tạo lại database với nguyên mục lục từ vankhan1.pdf...")
    print("=" * 60)
    
    # Kiểm tra file tồn tại
    if not PDF_PATH.exists():
        print(f"Không tìm thấy file: {PDF_PATH}")
        return
    
    # Khởi tạo database
    init_database()
    
    try:
        # Đọc text từ PDF
        print("1. Đọc PDF...")
        text = extract_text_from_pdf(PDF_PATH)
        print(f"   Đã đọc {len(text)} ký tự")
        
        # Trích xuất mục lục
        print("\n2. Trích xuất mục lục:")
        catalog = extract_catalog_from_pdf(text)
        print(f"   Tìm thấy {len(catalog)} mục trong mục lục")
        
        # Trích xuất nội dung
        print("\n3. Trích xuất nội dung:")
        prayers = extract_content_for_each_item(text, catalog)
        
        # Sắp xếp lại theo số thứ tự
        prayers.sort(key=lambda x: x['id'])
        
        # Lưu vào database
        print(f"\n4. Lưu vào database...")
        save_prayers_to_db(prayers)
        
        print(f"\n" + "=" * 60)
        print(f"HOÀN THÀNH! Đã tạo database với {len(prayers)} bài")
        print("=" * 60)
        
        print("\nDanh sách đầy đủ:")
        for i, prayer in enumerate(prayers, 1):
            print(f'{i:2d}. {prayer["id"]} - {prayer["title"]}')
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_complete_catalog()
