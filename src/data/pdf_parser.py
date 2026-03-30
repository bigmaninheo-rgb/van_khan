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


def extract_all_text_from_pdf(pdf_path: Path) -> str:
    """Đọc toàn bộ text từ PDF"""
    reader = PdfReader(pdf_path)
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text


def parse_prayers_from_text(text: str) -> List[Dict[str, Any]]:
    """Parse prayers từ text sử dụng multiple patterns"""
    prayers = []
    
    # Pattern 1: Tìm các dòng bắt đầu bằng "Văn khấn"
    pattern1 = re.compile(r'^(Văn khấn.+?)$', re.MULTILINE)
    matches1 = list(pattern1.finditer(text))
    
    if len(matches1) > 1:
        print(f"Tìm thấy {len(matches1)} tiêu đề Văn khấn")
        
        for i, match in enumerate(matches1):
            title = match.group(1).strip()
            start = match.end()
            
            # Tìm tiêu đề tiếp theo hoặc hết text
            end = matches1[i + 1].start() if i + 1 < len(matches1) else len(text)
            
            # Lấy nội dung giữa hai tiêu đề
            content = text[start:end].strip()
            
            # Chỉ lấy nếu có nội dung đủ dài
            if len(content) > 100:
                prayer_id = f"bai_{i + 1}"
                prayers.append({
                    'id': prayer_id,
                    'title': title,
                    'template': content
                })
    
    # Pattern 2: Tìm các dòng có chứa "Văn khấn" ở bất kỳ đâu
    if len(prayers) < 5:
        print("Thử pattern khác...")
        pattern2 = re.compile(r'(.+Văn khấn.+)', re.MULTILINE)
        matches2 = list(pattern2.finditer(text))
        
        for i, match in enumerate(matches2):
            title = match.group(1).strip()
            if len(title) < 200:  # Chỉ lấy các dòng tiêu đề ngắn
                prayer_id = f"bai_{len(prayers) + 1}"
                prayers.append({
                    'id': prayer_id,
                    'title': title,
                    'template': f"Nội dung cho {title}"
                })
    
    return prayers


def add_template_variables_to_prayers(prayers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Thêm các biến template vào prayers"""
    for prayer in prayers:
        template = prayer['template']
        
        # Replace common placeholders with template variables
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
        )
        
        prayer['template'] = template
    
    return prayers


def populate_database_from_vankhan1_pdf() -> None:
    """Điền dữ liệu vào database từ file vankhan1.pdf"""
    print("Đang khởi tạo database từ vankhan1.pdf...")
    
    # Kiểm tra file tồn tại
    if not PDF_PATH.exists():
        print(f"Không tìm thấy file: {PDF_PATH}")
        return
    
    # Khởi tạo database
    init_database()
    
    try:
        # Đọc toàn bộ text từ PDF
        print("Đang đọc toàn bộ nội dung PDF...")
        text = extract_all_text_from_pdf(PDF_PATH)
        print(f"Đã đọc {len(text)} ký tự từ PDF")
        
        # Parse prayers từ text
        prayers = parse_prayers_from_text(text)
        
        if not prayers:
            print("Không tìm thấy bài văn khấn nào")
            # Hiển thị 1000 ký tự đầu để debug
            print("Sample text:", text[:1000])
            return
        
        # Thêm template variables
        prayers = add_template_variables_to_prayers(prayers)
        
        # Lưu vào database
        save_prayers_to_db(prayers)
        
        print(f"\nĐã lưu {len(prayers)} bài văn khấn vào database từ vankhan1.pdf")
        print("Hoàn thành!")
        
    except Exception as e:
        print(f"Lỗi khi xử lý PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    populate_database_from_vankhan1_pdf()
