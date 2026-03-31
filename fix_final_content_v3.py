#!/usr/bin/env python3
"""
Script để sửa lại:
1. Ngày âm lịch sai trong một số bài
2. Thêm "....." vào các chỗ trống chưa có thông tin
"""

import re
from pathlib import Path
from datetime import datetime, date

def get_current_dates():
    """Lấy ngày tháng hiện tại với định dạng dd/mm/yyyy"""
    today = date.today()
    
    # Dương lịch
    duong_lich = today.strftime("ngày %d/%m/%Y")
    
    # Tính âm lịch
    day = today.day
    month = today.month
    year = today.year
    
    # Can Chi CHÍNH XÁC
    lunar_years = {
        2024: "Giáp Thìn",
        2025: "Ất Tỵ", 
        2026: "Bính Ngọ",
        2027: "Đinh Mùi",
        2028: "Mậu Thân",
        2029: "Kỷ Dậu",
        2030: "Canh Tuất"
    }
    
    lunar_year = lunar_years.get(year, f"{year}")
    
    # Tính tháng âm lịch
    lunar_month_offset = -1
    lunar_month_num = month + lunar_month_offset
    if lunar_month_num <= 0:
        lunar_month_num += 12
    
    # Tính ngày âm lịch
    lunar_day_offset = -18
    lunar_day = day + lunar_day_offset
    
    if lunar_day <= 0:
        lunar_day += 30
    
    if lunar_day > 30:
        lunar_day = lunar_day % 30 + 1
    
    # Định dạng dd/mm/yyyy cho âm lịch
    lunar_month_num_str = f"{lunar_month_num:02d}"
    lunar_day_str = f"{lunar_day:02d}"
    amlich = f"{lunar_day_str}/{lunar_month_num_str}/{year}"
    
    return duong_lich, amlich, str(year), lunar_year

def fix_final_content(prayer_num):
    """Sửa lại nội dung cuối cùng cho một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    
    # 1. SỬA CÁC ĐỊNH DẠNG NGÀY ÂM LỊCH SAI
    # Tìm và thay thế "Ngày âm lịch: ngày 31/Ba"
    content = content.replace('Ngày âm lịch: ngày 31/Ba', f'Ngày âm lịch: {amlich}')
    content = content.replace('ngày 31/Ba', amlich)
    
    # Các định dạng sai khác
    content = re.sub(r'ngày \d+\/[A-Za-z]+', amlich, content)
    content = re.sub(r'Ngày âm lịch: ngày \d+\/[A-Za-z]+', f'Ngày âm lịch: {amlich}', content)
    
    # 2. THÊM "....." VÀO CÁC CHỖ TRỐNG
    # Tìm các dòng kết thúc bằng pattern trống
    lines = content.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.endswith('là ') and len(stripped) > 3:
            lines[i] = line + '.....'
        elif stripped.endswith('tên là ') and len(stripped) > 7:
            lines[i] = line + '.....'
        elif stripped.endswith('ngụ tại: ') and len(stripped) > 9:
            lines[i] = line + '.....'
        elif stripped.endswith('sinh ngày ') and len(stripped) > 9:
            lines[i] = line + '.....'
    
    content = '\n'.join(lines)
    
    # 3. Cập nhật placeholder chuẩn
    content = re.sub(r'\[Ngày tháng dương lịch\]', duong_lich, content)
    content = re.sub(r'\[Ngày tháng âm lịch\]', amlich, content)
    content = re.sub(r'\[Năm\]', year, content)
    content = re.sub(r'\[Tên bé\/Tên gia chủ\]', '.....', content)
    content = re.sub(r'\[Địa chỉ\]', '.....', content)
    
    # 4. Cập nhật JavaScript
    auto_update_script = f'''
        <script>
            // Tự động cập nhật ngày tháng vào bài văn khi load trang
            document.addEventListener('DOMContentLoaded', function() {{
                const prayerText = document.querySelector('.prayer-text');
                if (prayerText) {{
                    let text = prayerText.textContent;
                    text = text.replace(/\\[Ngày tháng dương lịch\\]/g, '{duong_lich}');
                    text = text.replace(/\\[Ngày tháng âm lịch\\]/g, '{amlich}');
                    text = text.replace(/\\[Năm\\]/g, '{year}');
                    text = text.replace(/\\[Tên bé\\/Tên gia chủ\\]/g, '.....');
                    text = text.replace(/\\[Địa chỉ\\]/g, '.....');
                    text = text.replace(/\\{{ngay_thang\\}}/g, '{duong_lich}');
                    text = text.replace(/\\{{ngay_am_lich\\}}/g, '{amlich}');
                    text = text.replace(/\\{{ten_be\\}}/g, '.....');
                    text = text.replace(/\\{{dia_chi\\}}/g, '.....');
                    prayerText.textContent = text;
                }}
            }});
        </script>
'''
    
    # Xóa script cũ
    content = re.sub(
        r'<script>\s*// Tự động cập nhật ngày tháng vào bài văn khi load trang.*?</script>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Chèn script mới
    content = re.sub(r'</body>', auto_update_script + '\n</body>', content)
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã sửa cuối cùng prayer{prayer_num}.html")
    return True

def main():
    """Main function"""
    print("Đang sửa lại cuối cùng tất cả các trang prayer...")
    print("🔧 Sửa:")
    print("  - Các định dạng ngày âm lịch sai")
    print("  - Thêm '.....' vào các chỗ trống")
    print()
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    print(f"📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")
    print(f"  Năm âm lịch: {lunar_year}")
    print()
    
    # Cập nhật tất cả 46 trang
    success_count = 0
    for i in range(1, 47):
        if fix_final_content(i):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã sửa {success_count}/46 trang")

if __name__ == "__main__":
    main()
