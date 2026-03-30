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


def create_manual_catalog_from_pdf() -> List[Dict[str, Any]]:
    """Tạo mục lục thủ công dựa trên phân tích PDF"""
    
    # Mục lục thực sự từ vankhan1.pdf
    catalog = [
        # I. VĂN CÚNG NGÀY TẾT
        {"id": "tet_001", "title": "Văn cúng tạ mộ rước ông bà về ăn Tết"},
        {"id": "tet_002", "title": "Văn cúng lễ rước ông bà ngày 30 Tết"},
        {"id": "tet_003", "title": "Văn cúng ngày mồng 1 Tết"},
        {"id": "tet_004", "title": "Văn cúng hóa vàng ngày mồng 3 hết Tết"},
        {"id": "tet_005", "title": "Văn cúng lễ Nguyên tiêu (Rằm tháng giêng)"},
        {"id": "tet_006", "title": "Văn cúng lễ tảo mộ Tiết Thanh minh"},
        {"id": "tet_007", "title": "Văn cúng Tết Hàn thực"},
        {"id": "tet_008", "title": "Văn cúng Tết Đoan ngọ"},
        {"id": "tet_009", "title": "Văn cúng Rằm tháng 7"},
        {"id": "tet_010", "title": "Văn cúng Tết Trung thu"},
        {"id": "tet_011", "title": "Văn cúng Tết Hạ nguyên (Rằm tháng 10)"},
        {"id": "tet_012", "title": "Văn cúng ngày mồng 1 và 15 hàng tháng"},
        {"id": "tet_013", "title": "Văn cúng ngày mồng 2 và 16 hàng tháng"},
        
        # II. VĂN CÚNG THẦN TÀI, THỔ ĐỊA
        {"id": "than_001", "title": "Văn cúng Thần tài và Thổ địa"},
        {"id": "than_002", "title": "Văn cúng bàn thờ Thiên ngoài trời"},
        
        # III. VĂN CÚNG CÁC NGÀY GIỠ, TANG LỄ
        {"id": "gio_001", "title": "Văn cúng Bà Mụ ngày đầy cữ, đầy tháng, thôi nôi"},
        {"id": "gio_002", "title": "Văn cúng xin giải trừ bệnh tật"},
        {"id": "gio_003", "title": "Văn cúng cầu tự"},
        {"id": "gio_004", "title": "Văn cúng ngày lễ cưới hỏi"},
        {"id": "gio_005", "title": "Văn cúng lễ mừng thọ ông bà, cha mẹ"},
        {"id": "gio_006", "title": "Văn cúng lễ Cải táng, Bốc mộ, Cải cát"},
        {"id": "gio_007", "title": "Văn cúng lễ Tế ngu"},
        {"id": "gio_008", "title": "Văn cúng lễ Chung thất, Lễ Tốt khốc"},
        {"id": "gio_009", "title": "Văn cúng lễ cúng cơm hàng ngày"},
        {"id": "gio_010", "title": "Văn cúng lễ cúng cơm 100 ngày"},
        {"id": "gio_011", "title": "Văn cúng ngày giỗ hết (Đại tường)"},
        {"id": "gio_012", "title": "Văn cúng ngày giỗ thường hằng năm"},
        {"id": "gio_013", "title": "Văn cúng lễ ông Táo chầu trời ngày 23 tháng chạp"},
        {"id": "gio_014", "title": "Văn cúng lễ giao thừa: trong nhà & ngoài trời"},
        {"id": "gio_015", "title": "Văn cúng tất niên"},
        
        # IV. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIỾU
        {"id": "le_001", "title": "Văn cúng lễ Phật"},
        {"id": "le_002", "title": "Văn cúng Đức Ông - Đức Chúa Ông (Tôn giả Tu-đạt)"},
        {"id": "le_003", "title": "Văn cúng Đức Thánh Hiền (Đức A-nan-đà Tôn Giả)"},
        {"id": "le_004", "title": "Văn cúng cầu tài, cầu lộc, cầu bình an ở ban Tam Bảo"},
        {"id": "le_005", "title": "Văn cúng Bồ tát Quán Thế Âm"},
        {"id": "le_006", "title": "Văn cúng lễ Thánh mẫu"},
        {"id": "le_007", "title": "Văn cúng Thành hoàng"},
        {"id": "le_008", "title": "Văn cúng bà Tổ cô"},
        
        # V. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG
        {"id": "nha_001", "title": "Văn cúng lễ động thổ"},
        {"id": "nha_002", "title": "Văn cúng khi chuyển nhà, sửa nhà hàng"},
        {"id": "nha_003", "title": "Văn cúng lễ nhập trạch"},
        {"id": "nha_004", "title": "Văn cúng mừng tân gia"},
        {"id": "nha_005", "title": "Văn cúng lễ khai trương cửa hàng"},
        
        # VI. HƯỚNG DẪN CÁCH LỄ
        {"id": "hd_001", "title": "1. Đặt lễ vật: Thắp hương và làm lễ bàn thờ Đức Ông trước"},
        {"id": "hd_002", "title": "2. Sau khi đặt lễ ở bàn Đức Ông xong, đặt lễ lên hương án của chính điện, thắp đèn"},
        {"id": "hd_003", "title": "3. Sau khi đặt lễ chính điện xong thì đi thắp hương ở tất cả các bàn thờ khác của nhà"},
        {"id": "hd_004", "title": "4. Cuối cùng thì lễ ở nhà thờ Tổ (nhà Hậu)"},
        {"id": "hd_005", "title": "5. Cuối buổi lễ, sau khi đã lễ tạ để hạ lễ thì nên đến nhà trai giới hay phòng tiếp"},
    ]
    
    return catalog


def extract_content_for_catalog(text: str, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trích xuất nội dung cho từng mục trong mục lục"""
    
    print(f"Đang trích xuất nội dung cho {len(catalog)} mục...")
    
    results = []
    
    for item in catalog:
        title = item['title']
        
        # Tạo pattern để tìm tiêu đề
        escaped_title = re.escape(title)
        pattern = re.compile(f'{escaped_title}', re.IGNORECASE)
        
        match = pattern.search(text)
        if match:
            start_pos = match.start()
            
            # Tìm vị trí kết thúc (tiêu đề tiếp theo)
            end_pos = len(text)
            
            # Lấy nội dung
            content = text[start_pos:start_pos + 2000].strip()  # Giới hạn 2000 ký tự
            
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
            print(f'  ✓ {title}')
        else:
            # Dùng placeholder nếu không tìm thấy
            results.append({
                'id': item['id'],
                'title': item['title'],
                'template': f'Nội dung cho {title}'
            })
            print(f'  - {title} (placeholder)')
    
    return results


def create_complete_pdf_catalog() -> None:
    """Tạo database với nguyên mục lục từ PDF"""
    print("Đang tạo database với NGUYÊN MỤC LỤC từ vankhan1.pdf")
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
        
        # Tạo mục lục thủ công
        print("\n2. Tạo mục lục theo PDF:")
        catalog = create_manual_catalog_from_pdf()
        print(f"   Tạo {len(catalog)} mục")
        
        # Trích xuất nội dung
        print("\n3. Trích xuất nội dung:")
        prayers = extract_content_for_catalog(text, catalog)
        
        # Lưu vào database
        print(f"\n4. Lưu vào database...")
        save_prayers_to_db(prayers)
        
        print(f"\n" + "=" * 60)
        print(f"HOÀN THÀNH! Đã tạo database với {len(prayers)} bài")
        print("=" * 60)
        
        # Hiển thị theo nhóm
        groups = {
            "I. VĂN CÚNG NGÀY TẾT": [],
            "II. VĂN CÚNG THẦN TÀI, THỔ ĐỊA": [], 
            "III. VĂN CÚNG CÁC NGÀY GIỠ, TANG LỄ": [],
            "IV. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIỾU": [],
            "V. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG": [],
            "VI. HƯỚNG DẪN CÁCH LỄ": []
        }
        
        for prayer in prayers:
            if prayer['id'].startswith('tet_'):
                groups["I. VĂN CÚNG NGÀY TẾT"].append(prayer)
            elif prayer['id'].startswith('than_'):
                groups["II. VĂN CÚNG THẦN TÀI, THỔ ĐỊA"].append(prayer)
            elif prayer['id'].startswith('gio_'):
                groups["III. VĂN CÚNG CÁC NGÀY GIỠ, TANG LỄ"].append(prayer)
            elif prayer['id'].startswith('le_'):
                groups["IV. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIỾU"].append(prayer)
            elif prayer['id'].startswith('nha_'):
                groups["V. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG"].append(prayer)
            elif prayer['id'].startswith('hd_'):
                groups["VI. HƯỚNG DẪN CÁCH LỄ"].append(prayer)
        
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
    create_complete_pdf_catalog()
