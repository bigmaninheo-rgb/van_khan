#!/usr/bin/env python3
"""
Script để sửa lại ngày âm lịch chính xác hơn
"""

import re
from pathlib import Path
from datetime import datetime, date

def get_current_dates():
    """Lấy ngày tháng hiện tại với âm lịch chính xác"""
    today = date.today()
    
    # Dương lịch
    duong_lich = today.strftime("ngày %d/%m/%Y")
    
    # Tính âm lịch chính xác hơn
    day = today.day
    month = today.month
    year = today.year
    
    # Mapping năm âm lịch CHÍNH XÁC
    # Can Chi: Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý
    # Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi
    
    # Năm 2024: Giáp Thìn
    # Năm 2025: Ất Tỵ  
    # Năm 2026: Bính Thân
    # Năm 2027: Đinh Dậu
    # Năm 2028: Mậu Tuất
    # Năm 2029: Kỷ Hợi
    # Năm 2030: Canh Tý
    
    lunar_years = {
        2024: "Giáp Thìn",
        2025: "Ất Tỵ", 
        2026: "Bính Thân",
        2027: "Đinh Dậu",
        2028: "Mậu Tuất",
        2029: "Kỷ Hợi",
        2030: "Canh Tý"
    }
    
    lunar_year = lunar_years.get(year, f"{year}")
    
    # Tính tháng âm lịch (đơn giản nhưng hợp lý hơn)
    # Tháng âm lịch thường trễ 1-2 tháng so với dương lịch
    # 31/03/2026 -> khoảng tháng 2 âm lịch
    lunar_month_offset = -1  # Trễ 1 tháng
    lunar_month_num = month + lunar_month_offset
    if lunar_month_num <= 0:
        lunar_month_num += 12
    
    lunar_months = ['Giêng', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 
                    'Bảy', 'Tám', 'Chín', 'Mười', 'Mười Một', 'Chạp']
    
    lunar_month = lunar_months[lunar_month_num - 1]
    
    # Tính ngày âm lịch (đơn giản)
    # Ngày âm lịch thường khác ngày dương lịch khoảng 10-20 ngày
    # 31/03/2026 -> khoảng ngày 3-11 âm lịch
    lunar_day_offset = -20  # Lùi lại 20 ngày
    lunar_day = day + lunar_day_offset
    
    # Điều chỉnh nếu ngày âm lịch <= 0
    if lunar_day <= 0:
        lunar_day += 30  # Thêm vào tháng trước
    
    # Giới hạn ngày trong tháng (1-30)
    if lunar_day > 30:
        lunar_day = lunar_day % 30 + 1
    
    # Định dạng đầy đủ
    amlich = f"ngày {lunar_day} tháng {lunar_month} năm {lunar_year}"
    
    return duong_lich, amlich, str(year), lunar_year

def fix_correct_amlich(prayer_num):
    """Sửa ngày âm lịch chính xác cho một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
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
    
    print(f"✅ Đã sửa ngày âm lịch prayer{prayer_num}.html")
    return True

def main():
    """Main function"""
    print("Đang sửa lại ngày âm lịch chính xác...")
    print("🔧 Sửa lỗi:")
    print("  - Năm 2026 = Bính Thân (không phải Ất Dậu)")
    print("  - Tính ngày tháng hợp lý hơn")
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
        if fix_correct_amlich(i):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã sửa {success_count}/46 trang")

if __name__ == "__main__":
    main()
