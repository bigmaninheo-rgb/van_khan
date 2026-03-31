#!/usr/bin/env python3
"""
Script để sửa lại định dạng ngày âm lịch cho các trang prayer gốc
"""

import re
from pathlib import Path
from datetime import datetime, date

def get_current_dates():
    """Lấy ngày tháng hiện tại với âm lịch đầy đủ"""
    today = date.today()
    
    # Dương lịch
    duong_lich = today.strftime("ngày %d/%m/%Y")
    
    # Tính âm lịch chính xác hơn
    day = today.day
    month = today.month
    year = today.year
    
    # Mapping năm âm lịch
    lunar_years = {
        2024: "Quý Mão",
        2025: "Giáp Thìn", 
        2026: "Ất Dậu",
        2027: "Bính Tuất",
        2028: "Đinh Hợi",
        2029: "Mậu Tý",
        2030: "Kỷ Sửu"
    }
    
    lunar_year = lunar_years.get(year, f"{year}")
    
    # Tính tháng âm lịch
    lunar_month_offset = -1
    lunar_month_num = month + lunar_month_offset
    if lunar_month_num <= 0:
        lunar_month_num += 12
    
    lunar_months = ['Giêng', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 
                    'Bảy', 'Tám', 'Chín', 'Mười', 'Mười Một', 'Chạp']
    
    lunar_month = lunar_months[lunar_month_num - 1]
    
    # Tính ngày âm lịch
    lunar_day_offset = -10
    lunar_day = day + lunar_day_offset
    
    if lunar_day <= 0:
        lunar_day += 30
    
    if lunar_day > 30:
        lunar_day = lunar_day % 30 + 1
    
    # Định dạng đầy đủ: ngày 21 tháng Hai năm Ất Dậu
    amlich = f"ngày {lunar_day} tháng {lunar_month} năm {lunar_year}"
    
    return duong_lich, amlich, str(year), lunar_year

def fix_original_amlich_format(file_name):
    """Sửa định dạng ngày âm lịch cho một trang prayer gốc"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/{file_name}")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    
    # 1. Thay thế placeholder ngay trong HTML content
    content = re.sub(
        r'\[Ngày tháng dương lịch\]',
        duong_lich,
        content
    )
    
    content = re.sub(
        r'\[Ngày tháng âm lịch\]',
        amlich,
        content
    )
    
    content = re.sub(
        r'\[Năm\]',
        year,
        content
    )
    
    # 2. Xóa các placeholder khác
    content = re.sub(
        r'\[Tên bé\/Tên gia chủ\]',
        '',
        content
    )
    
    content = re.sub(
        r'\[Địa chỉ\]',
        '',
        content
    )
    
    # 3. Cập nhật JavaScript
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
                    text = text.replace(/\\[Tên bé\\/Tên gia chủ\\]/g, '');
                    text = text.replace(/\\[Địa chỉ\\]/g, '');
                    text = text.replace(/\\{{ngay_thang\\}}/g, '{duong_lich}');
                    text = text.replace(/\\{{ngay_am_lich\\}}/g, '{amlich}');
                    text = text.replace(/\\{{ten_be\\}}/g, '');
                    text = text.replace(/\\{{dia_chi\\}}/g, '');
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
    content = re.sub(
        r'</body>',
        auto_update_script + '\n</body>',
        content
    )
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã sửa định dạng {file_name}")
    return True

def main():
    """Main function"""
    print("Đang sửa lại định dạng ngày âm lịch cho các trang prayer gốc...")
    print()
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    print(f"📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")
    print(f"  Năm âm lịch: {lunar_year}")
    print()
    
    # Danh sách các file prayer gốc
    original_files = [
        "prayerI_001.html", "prayerI_002.html", "prayerI_003.html", "prayerI_004.html", "prayerI_005.html",
        "prayerII_006.html", "prayerII_007.html", "prayerII_008.html", "prayerII_009.html", "prayerII_010.html",
        "prayerII_011.html", "prayerII_012.html", "prayerII_013.html", "prayerII_014.html",
        "prayerIII_015.html", "prayerIII_016.html", "prayerIII_017.html", "prayerIII_018.html", "prayerIII_019.html",
        "prayerIII_020.html", "prayerIII_021.html",
        "prayerIV_022.html", "prayerIV_023.html", "prayerIV_024.html", "prayerIV_025.html", "prayerIV_026.html",
        "prayerIV_027.html", "prayerIV_028.html", "prayerIV_029.html", "prayerIV_030.html", "prayerIV_031.html",
        "prayerIV_032.html", "prayerIV_033.html",
        "prayerV_034.html", "prayerV_035.html", "prayerV_036.html", "prayerV_037.html", "prayerV_038.html",
        "prayerV_039.html", "prayerV_040.html", "prayerV_041.html",
        "prayerVI_042.html", "prayerVI_043.html", "prayerVI_044.html", "prayerVI_045.html", "prayerVI_046.html"
    ]
    
    # Cập nhật tất cả các file
    success_count = 0
    for file_name in original_files:
        if fix_original_amlich_format(file_name):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã sửa {success_count}/{len(original_files)} trang prayer gốc")

if __name__ == "__main__":
    main()
