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


def parse_all_prayers_from_text(text: str) -> List[Dict[str, Any]]:
    """Parse tất cả prayers từ text với nhiều pattern khác nhau"""
    prayers = []
    
    # Pattern 1: Tìm các dòng bắt đầu bằng "Văn khấn"
    pattern1 = re.compile(r'^(Văn khấn.+?)$', re.MULTILINE)
    matches1 = list(pattern1.finditer(text))
    
    print(f"Pattern 1: Tìm thấy {len(matches1)} dòng bắt đầu bằng 'Văn khấn'")
    
    for i, match in enumerate(matches1):
        title = match.group(1).strip()
        start = match.end()
        
        # Tìm tiêu đề tiếp theo hoặc hết text
        end = matches1[i + 1].start() if i + 1 < len(matches1) else len(text)
        
        # Lấy nội dung giữa hai tiêu đề
        content = text[start:end].strip()
        
        # Lọc nội dung có ý nghĩa
        if len(content) > 50:
            prayer_id = f"vk_{i + 1}"
            prayers.append({
                'id': prayer_id,
                'title': title,
                'template': content
            })
    
    # Pattern 2: Tìm các pattern khác có thể là tiêu đề
    patterns = [
        r'^(Văn\s+khấn.+?)$',  # Văn khấn với khoảng cách
        r'^(\d+\.\s*Văn\s+khấn.+?)$',  # Số thứ tự. Văn khấn
        r'^(\d+\)\s*Văn\s+khấn.+?)$',  # Số thứ tự) Văn khấn
        r'^(Văn\s+cúng.+?)$',  # Văn cúng
        r'^(Văn\s+khai.+?)$',  # Văn khai
        r'^(\d+\.\s*.+?)$',  # Các dòng có số thứ tự
    ]
    
    for pattern_idx, pattern in enumerate(patterns[1:], 2):
        if len(prayers) >= 20:  # Giới hạn để tránh quá nhiều
            break
            
        regex = re.compile(pattern, re.MULTILINE)
        matches = list(regex.finditer(text))
        
        print(f"Pattern {pattern_idx}: Tìm thấy {len(matches)} kết quả")
        
        for match in matches:
            title = match.group(1).strip()
            
            # Bỏ qua nếu quá ngắn hoặc quá dài
            if len(title) < 10 or len(title) > 200:
                continue
                
            # Bỏ qua nếu đã có trong danh sách
            if any(p['title'] == title for p in prayers):
                continue
            
            # Tìm nội dung sau tiêu đề
            start = match.end()
            end = len(text)
            
            # Tìm tiêu đề tiếp theo
            for other_pattern in patterns:
                other_regex = re.compile(other_pattern, re.MULTILINE)
                other_matches = list(other_regex.finditer(text[start:]))
                if other_matches:
                    end = start + other_matches[0].start()
                    break
            
            content = text[start:end].strip()
            
            if len(content) > 50:
                prayer_id = f"pk_{pattern_idx}_{len(prayers) + 1}"
                prayers.append({
                    'id': prayer_id,
                    'title': title,
                    'template': content
                })
    
    # Pattern 3: Tìm theo từ khóa đặc biệt
    keywords = ['Văn khấn', 'Văn cúng', 'Văn khai', 'Văn tế', 'Vãn tế']
    
    for keyword in keywords:
        if len(prayers) >= 30:
            break
            
        pattern = re.compile(f'^(.*{keyword}.+?)$', re.MULTILINE)
        matches = list(pattern.finditer(text))
        
        for match in matches:
            title = match.group(1).strip()
            
            if len(title) < 10 or len(title) > 200:
                continue
                
            if any(p['title'] == title for p in prayers):
                continue
            
            prayer_id = f"kw_{len(prayers) + 1}"
            prayers.append({
                'id': prayer_id,
                'title': title,
                'template': f"Nội dung cho {title}"
            })
    
    return prayers


def clean_and_format_prayers(prayers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Làm sạch và định dạng prayers"""
    cleaned_prayers = []
    
    for prayer in prayers:
        title = prayer['title'].strip()
        template = prayer['template'].strip()
        
        # Làm sạch tiêu đề
        title = re.sub(r'\s+', ' ', title)  # Thay thế nhiều khoảng trắng
        title = title.replace('\n', ' ')  # Xóa xuống dòng trong tiêu đề
        
        # Làm sạch nội dung
        template = re.sub(r'\n\s*\n', '\n\n', template)  # Chuẩn hóa xuống dòng
        template = re.sub(r'[ ]{2,}', ' ', template)  # Thay thế nhiều khoảng trắng
        
        # Thêm template variables
        template = template.replace(
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
        if len(template) > 100:
            cleaned_prayers.append({
                'id': prayer['id'],
                'title': title,
                'template': template
            })
    
    return cleaned_prayers


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
        
        # Parse tất cả prayers từ text
        prayers = parse_all_prayers_from_text(text)
        
        if not prayers:
            print("Không tìm thấy bài văn khấn nào")
            return
        
        # Làm sạch và định dạng
        prayers = clean_and_format_prayers(prayers)
        
        # Lưu vào database
        save_prayers_to_db(prayers)
        
        print(f"\nĐã lưu {len(prayers)} bài văn khấn vào database từ vankhan1.pdf")
        
        # Hiển thị danh sách
        print("\nDanh sách các bài:")
        for i, prayer in enumerate(prayers, 1):
            print(f"{i}. {prayer['title']}")
        
        print("\nHoàn thành!")
        
    except Exception as e:
        print(f"Lỗi khi xử lý PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    populate_database_from_vankhan1_pdf()
