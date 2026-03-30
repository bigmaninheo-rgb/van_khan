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
    """Đọc text từ PDF"""
    reader = PdfReader(pdf_path)
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text


def parse_catalog_from_text(text: str) -> List[Dict[str, Any]]:
    """Parse mục lục từ text PDF theo đúng cấu trúc"""
    
    # Tìm phần mục lục - thường ở đầu PDF
    lines = text.split('\n')
    
    # Tìm các dòng có số thứ tự (1., 2., 3., ...)
    catalog_items = []
    
    # Pattern để tìm mục lục: số. + tên bài
    catalog_pattern = re.compile(r'^(\d+)\.\s*(.+)$')
    
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
                    'id': f'bai_{number:03d}',  # ID theo thứ tự: bai_001, bai_002...
                    'title': title,
                    'template': f'Nội dung cho {title}'  # Placeholder
                })
    
    return catalog_items


def extract_full_content_for_prayers(text: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trích xuất nội dung đầy đủ cho mỗi bài"""
    
    # Tìm tất cả các tiêu đề trong text
    title_patterns = []
    for item in catalog:
        # Tạo pattern để tìm tiêu đề trong text
        title = item['title']
        # Escape các ký tự đặc biệt trong regex
        escaped_title = re.escape(title)
        pattern = re.compile(f'{escaped_title}', re.IGNORECASE)
        title_patterns.append((item['id'], pattern))
    
    # Sắp xếp theo vị trí xuất hiện trong text
    found_positions = []
    for prayer_id, pattern in title_patterns:
        match = pattern.search(text)
        if match:
            found_positions.append((prayer_id, match.start(), pattern))
    
    # Sắp xếp theo vị trí
    found_positions.sort(key=lambda x: x[1])
    
    # Trích xuất nội dung giữa các tiêu đề
    results = []
    for i, (prayer_id, start_pos, pattern) in enumerate(found_positions):
        # Tìm vị trí kết thúc (tiêu đề tiếp theo)
        end_pos = len(text)
        if i + 1 < len(found_positions):
            end_pos = found_positions[i + 1][1]
        
        # Lấy nội dung
        content = text[start_pos:end_pos].strip()
        
        # Tìm item trong catalog
        catalog_item = next((item for item in catalog if item['id'] == prayer_id), None)
        if catalog_item:
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
            
            results.append({
                'id': prayer_id,
                'title': catalog_item['title'],
                'template': content
            })
    
    return results


def create_manual_catalog() -> List[Dict[str, Any]]:
    """Tạo mục lục thủ công theo đúng PDF"""
    
    # Danh sách theo đúng thứ tự trong PDF vankhan1.pdf
    catalog = [
        {"id": "bai_001", "title": "Văn khấn Thổ Thần, Táo Quân, Long Mạch và các vị Thần linh trước khi"},
        {"id": "bai_002", "title": "Văn khấn cầu tài, cầu lộc, cầu bình an ở ban Tam Bảo (Phật Bảo, Pháp Bảo, Tăng Bảo)"},
        {"id": "bai_003", "title": "Văn cúng tạ mộ rước ông bà về ăn Tết"},
        {"id": "bai_004", "title": "Văn cúng lễ rước ông bà ngày 30 Tết"},
        {"id": "bai_005", "title": "Văn cúng ngày mồng 1 Tết"},
        {"id": "bai_006", "title": "Văn cúng hóa vàng ngày mồng 3 hết Tết"},
        {"id": "bai_007", "title": "Văn cúng lễ Nguyên tiêu (Rằm tháng giêng)"},
        {"id": "bai_008", "title": "Văn cúng lễ tảo mộ Tiết Thanh minh"},
        {"id": "bai_009", "title": "Văn cúng Tết Hàn thực"},
        {"id": "bai_010", "title": "Văn cúng Tết Đoan ngọ"},
        {"id": "bai_011", "title": "Văn cúng Rằm tháng 7"},
        {"id": "bai_012", "title": "Văn cúng Tết Trung thu"},
        {"id": "bai_013", "title": "Văn cúng Tết Hạ nguyên (Rằm tháng 10)"},
        {"id": "bai_014", "title": "Văn cúng ngày mồng 1 và 15 hàng tháng"},
        {"id": "bai_015", "title": "Văn cúng ngày mồng 2 và 16 hàng tháng"},
        {"id": "bai_016", "title": "Văn cúng Thần tài và Thổ địa"},
        {"id": "bai_017", "title": "Văn cúng bàn thờ Thiên ngoài trời"},
        {"id": "bai_018", "title": "Văn cúng Lễ phóng sinh"},
        {"id": "bai_019", "title": "Văn cúng lễ Phật"},
        {"id": "bai_020", "title": "Văn cúng Đức Ông - Đức Chúa Ông (Tôn giả Tu-đạt)"},
        {"id": "bai_021", "title": "Văn cúng Đức Thánh Hiền (Đức A-nan-đà Tôn Giả)"},
        {"id": "bai_022", "title": "Văn cúng cầu tài, cầu lộc, cầu bình an ở ban Tam Bảo"},
        {"id": "bai_023", "title": "Văn cúng Bồ tát Quán Thế Âm"},
        {"id": "bai_024", "title": "Văn cúng lễ Thánh mẫu"},
        {"id": "bai_025", "title": "Văn cúng Thành hoàng"},
        {"id": "bai_026", "title": "Văn cúng bà Tổ cô"},
        {"id": "bai_027", "title": "Văn cúng lễ động thổ"},
        {"id": "bai_028", "title": "Văn cúng khi chuyển nhà, sửa nhà hàng"},
        {"id": "bai_029", "title": "Văn cúng lễ nhập trạch"},
        {"id": "bai_030", "title": "Văn cúng mừng tân gia"},
        {"id": "bai_031", "title": "Văn cúng lễ khai trương cửa hàng"},
        {"id": "bai_032", "title": "Văn cúng Bà Mụ ngày đầy cữ, đầy tháng, thôi nôi"},
        {"id": "bai_033", "title": "Văn cúng xin giải trừ bệnh tật"},
        {"id": "bai_034", "title": "Văn cúng cầu tự"},
        {"id": "bai_035", "title": "Văn cúng ngày lễ cưới hỏi"},
        {"id": "bai_036", "title": "Văn cúng lễ mừng thọ ông bà, cha mẹ"},
        {"id": "bai_037", "title": "Văn cúng lễ Cải táng, Bốc mộ, Cải cát"},
        {"id": "bai_038", "title": "Văn cúng lễ Tế ngu"},
        {"id": "bai_039", "title": "Văn cúng lễ Chung thất, Lễ Tốt khốc"},
        {"id": "bai_040", "title": "Văn cúng lễ cúng cơm hàng ngày"},
        {"id": "bai_041", "title": "Văn cúng lễ cúng cơm 100 ngày"},
        {"id": "bai_042", "title": "Văn cúng ngày giỗ hết (Đại tường)"},
        {"id": "bai_043", "title": "Văn cúng ngày giỗ thường hằng năm"},
        {"id": "bai_044", "title": "Văn cúng lễ ông Táo chầu trời ngày 23 tháng chạp"},
        {"id": "bai_045", "title": "Văn cúng lễ giao thừa: trong nhà & ngoài trời"},
        {"id": "bai_046", "title": "Văn cúng tất niên"},
    ]
    
    return catalog


def populate_database_correctly() -> None:
    """Tạo lại database đúng theo mục lục PDF"""
    print("Đang tạo lại database đúng theo mục lục PDF...")
    
    # Kiểm tra file tồn tại
    if not PDF_PATH.exists():
        print(f"Không tìm thấy file: {PDF_PATH}")
        return
    
    # Khởi tạo database
    init_database()
    
    try:
        # Đọc text từ PDF
        print("Đang đọc PDF...")
        text = extract_text_from_pdf(PDF_PATH)
        print(f"Đã đọc {len(text)} ký tự")
        
        # Tạo mục lục thủ công đúng theo PDF
        catalog = create_manual_catalog()
        print(f"Đã tạo mục lục với {len(catalog)} bài")
        
        # Trích xuất nội dung đầy đủ
        print("Đang trích xuất nội dung...")
        prayers = extract_full_content_for_prayers(text, catalog)
        
        print(f"Đã trích xuất nội dung cho {len(prayers)} bài")
        
        # Nếu không trích xuất được nội dung, dùng mục lục với placeholder
        if len(prayers) < len(catalog):
            print("Một số bài không có nội dung, sử dụng placeholder...")
            for item in catalog:
                if not any(p['id'] == item['id'] for p in prayers):
                    prayers.append({
                        'id': item['id'],
                        'title': item['title'],
                        'template': f'Nội dung cho {item["title"]}'
                    })
        
        # Lưu vào database
        save_prayers_to_db(prayers)
        
        print(f"\nĐã lưu {len(prayers)} bài vào database")
        print("\nDanh sách các bài:")
        for i, prayer in enumerate(prayers, 1):
            print(f'{i:2d}. {prayer["id"]} - {prayer["title"]}')
        
        print("\nHoàn thành!")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    populate_database_correctly()
