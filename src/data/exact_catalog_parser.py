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


def create_exact_catalog_from_pdf() -> List[Dict[str, Any]]:
    """Tạo mục lục chính xác theo PDF bạn cung cấp"""
    
    # Mục lục chính xác từ PDF với số trang
    catalog = [
        # MỞ ĐẦU
        {"id": "intro_001", "title": "Ý nghĩa của cúng, khấn, vái, và lạy", "page": 1},
        {"id": "intro_002", "title": "Cách thắp hương của người Việt", "page": 4},
        
        # I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG
        {"id": "mh_001", "title": "Văn cúng Bà Mụ ngày đầy cữ, đầy tháng, thôi nôi", "page": 7},
        {"id": "mh_002", "title": "Văn cúng xin giải trừ bệnh tật", "page": 8},
        {"id": "mh_003", "title": "Văn cúng cầu tự", "page": 9},
        {"id": "mh_004", "title": "Văn cúng ngày lễ cưới hỏi", "page": 10},
        {"id": "mh_005", "title": "Văn cúng lễ mừng thọ ông bà, cha mẹ", "page": 11},
        
        # II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN
        {"id": "tg_001", "title": "Văn cúng lễ Cải táng, Bốc mộ, Cải cát", "page": 13},
        {"id": "tg_002", "title": "Văn cúng lễ Tế ngu", "page": 14},
        {"id": "tg_003", "title": "Văn cúng lễ Chung thất, Lễ Tốt khốc", "page": 15},
        {"id": "tg_004", "title": "Văn cúng lễ cúng cơm hàng ngày", "page": 17},
        {"id": "tg_005", "title": "Văn cúng lễ cúng cơm 100 ngày", "page": 18},
        {"id": "tg_006", "title": "Văn cúng ngày giỗ đầu (Tiểu tường)", "page": 19},
        {"id": "tg_007", "title": "Văn cúng ngày giỗ hết (Đại tường)", "page": 21},
        {"id": "tg_008", "title": "Văn cúng ngày giỗ thường hằng năm", "page": 23},
        {"id": "tg_009", "title": "Văn cúng ngày cáo giỗ (ngày Tiên thường)", "page": 25},
        
        # III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN
        {"id": "td_001", "title": "Văn cúng lễ ông Táo chầu trời ngày 23 tháng chạp", "page": 28},
        {"id": "td_002", "title": "Văn cúng lễ giao thừa: trong nhà & ngoài trời", "page": 29},
        {"id": "td_003", "title": "Văn cúng tất niên", "page": 32},
        {"id": "td_004", "title": "Văn cúng tạ mộ rước ông bà về ăn Tết", "page": 33},
        {"id": "td_005", "title": "Văn cúng lễ rước ông bà ngày 30 Tết", "page": 34},
        {"id": "td_006", "title": "Văn cúng ngày mồng 1 Tết", "page": 35},
        {"id": "td_007", "title": "Văn cúng hóa vàng ngày mồng 3 hết Tết", "page": 36},
        
        # IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC
        {"id": "kh_001", "title": "Văn cúng lễ Nguyên tiêu (Rằm tháng giêng)", "page": 41},
        {"id": "kh_002", "title": "Văn cúng lễ tảo mộ Tiết Thanh minh", "page": 43},
        {"id": "kh_003", "title": "Văn cúng Tết Hàn thực", "page": 45},
        {"id": "kh_004", "title": "Văn cúng Tết Đoan ngọ", "page": 46},
        {"id": "kh_005", "title": "Văn cúng Rằm tháng 7", "page": 47},
        {"id": "kh_006", "title": "Văn cúng Tết Trung thu", "page": 50},
        {"id": "kh_007", "title": "Văn cúng Tết Hạ nguyên (Rằm tháng 10)", "page": 51},
        {"id": "kh_008", "title": "Văn cúng ngày mồng 1 và 15 hàng tháng", "page": 52},
        {"id": "kh_009", "title": "Văn cúng ngày mồng 2 và 16 hàng tháng", "page": 54},
        {"id": "kh_010", "title": "Văn cúng Thần tài và Thổ địa", "page": 56},
        {"id": "kh_011", "title": "Văn cúng bàn thờ Thiên ngoài trời", "page": 56},
        {"id": "kh_012", "title": "Văn cúng Lễ phóng sinh", "page": 57},
        
        # V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU
        {"id": "cm_001", "title": "Văn cúng lễ Phật", "page": 60},
        {"id": "cm_002", "title": "Văn cúng Đức Ông - Đức Chúa Ông (Tôn giả Tu-đạt)", "page": 60},
        {"id": "cm_003", "title": "Văn cúng Đức Thánh Hiền (Đức A-nan-đà Tôn Giả)", "page": 61},
        {"id": "cm_004", "title": "Văn cúng cầu tài, cầu lộc, cầu bình an ở ban Tam Bảo", "page": 62},
        {"id": "cm_005", "title": "Văn cúng Bồ tát Quán Thế Âm", "page": 63},
        {"id": "cm_006", "title": "Văn cúng lễ Thánh mẫu", "page": 64},
        {"id": "cm_007", "title": "Văn cúng Thành hoàng", "page": 64},
        {"id": "cm_008", "title": "Văn cúng bà Tổ cô", "page": 65},
        
        # VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG
        {"id": "nh_001", "title": "Văn cúng lễ động thổ", "page": 67},
        {"id": "nh_002", "title": "Văn cúng khi chuyển nhà, sửa nhà hàng", "page": 68},
        {"id": "nh_003", "title": "Văn cúng lễ nhập trạch", "page": 69},
        {"id": "nh_004", "title": "Văn cúng mừng tân gia", "page": 71},
        {"id": "nh_005", "title": "Văn cúng lễ khai trương cửa hàng", "page": 73},
    ]
    
    return catalog


def extract_content_by_page(text: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trích xuất nội dung theo số trang"""
    
    print(f"Đang trích xuất nội dung theo số trang cho {len(catalog)} mục...")
    
    results = []
    
    for item in catalog:
        title = item['title']
        page_num = item['page']
        
        # Tạo pattern để tìm tiêu đề
        escaped_title = re.escape(title)
        pattern = re.compile(f'{escaped_title}', re.IGNORECASE)
        
        match = pattern.search(text)
        if match:
            start_pos = match.start()
            
            # Tìm vị trí kết thúc (tiêu đề tiếp theo hoặc khoảng 2000 ký tự)
            end_pos = start_pos + 2000
            
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
            
            results.append({
                'id': item['id'],
                'title': item['title'],
                'template': content
            })
            print(f'  ✓ [Trang {page_num:2d}] {title}')
        else:
            # Dùng placeholder nếu không tìm thấy
            results.append({
                'id': item['id'],
                'title': item['title'],
                'template': f'Nội dung cho {title} (trang {page_num})'
            })
            print(f'  - [Trang {page_num:2d}] {title} (placeholder)')
    
    return results


def create_exact_pdf_catalog() -> None:
    """Tạo database với mục lục chính xác theo PDF"""
    print("Đang tạo database với MỤC LỤC CHÍNH XÁC từ PDF")
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
        
        # Tạo mục lục chính xác
        print("\n2. Tạo mục lục chính xác theo PDF:")
        catalog = create_exact_catalog_from_pdf()
        print(f"   Tạo {len(catalog)} mục")
        
        # Trích xuất nội dung
        print("\n3. Trích xuất nội dung theo trang:")
        prayers = extract_content_by_page(text, catalog)
        
        # Lưu vào database
        print(f"\n4. Lưu vào database...")
        save_prayers_to_db(prayers)
        
        print(f"\n" + "=" * 60)
        print(f"HOÀN THÀNH! Đã tạo database với {len(prayers)} bài")
        print("=" * 60)
        
        # Hiển thị theo nhóm
        groups = {
            "GIỚI THIỆU": [],
            "I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG": [],
            "II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN": [],
            "III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN": [],
            "IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC": [],
            "V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU": [],
            "VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG": []
        }
        
        for prayer in prayers:
            if prayer['id'].startswith('intro_'):
                groups["GIỚI THIỆU"].append(prayer)
            elif prayer['id'].startswith('mh_'):
                groups["I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG"].append(prayer)
            elif prayer['id'].startswith('tg_'):
                groups["II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN"].append(prayer)
            elif prayer['id'].startswith('td_'):
                groups["III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN"].append(prayer)
            elif prayer['id'].startswith('kh_'):
                groups["IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC"].append(prayer)
            elif prayer['id'].startswith('cm_'):
                groups["V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU"].append(prayer)
            elif prayer['id'].startswith('nh_'):
                groups["VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG"].append(prayer)
        
        for group_name, items in groups.items():
            if items:
                print(f"\n{group_name}:")
                for i, item in enumerate(items, 1):
                    print(f"  {i}. {item['title']}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_exact_pdf_catalog()
