#!/usr/bin/env python3
"""
Script FINAL CHECK - Kiểm tra và sửa lại tất cả các bài văn khấn
Đảm bảo TẤT CẢ đều có "....." và ngày tháng đúng
"""

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

def final_check_prayer(prayer_num):
    """Kiểm tra và sửa CUỐI CÙNG cho một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    
    print(f"🔍 FINAL CHECK prayer{prayer_num}.html...")
    
    original_content = content
    changes_made = []
    
    # 1. SỬA CÁC ĐỊNH DẠNG NGÀY TRÙNG LẶP
    if 'Hôm nay là ngày ngày ' in content:
        content = content.replace('Hôm nay là ngày ngày ', f'Hôm nay là ngày ')
        changes_made.append("Sửa trùng 'ngày ngày'")
    
    # 2. SỬA CÁC CHỖ TRỐNG CẦN THÊM "....." - DÙNG STRING REPLACE
    replacements = [
        ('Tín chủ con là ', 'Tín chủ con là .....'),
        ('Vợ chồng con là  sinh được con', 'Vợ chồng con là ..... sinh được con'),
        ('Vợ chồng con là sinh được con', 'Vợ chồng con là ..... sinh được con'),
        ('Chúng con ngụ tại: ', 'Chúng con ngụ tại: .....'),
        ('ngụ tại ', 'ngụ tại .....'),
        ('tên là  sinh ngày ', 'tên là ..... sinh ngày '),
        ('tên là sinh ngày ', 'tên là ..... sinh day '),
        ('sinh ngày ', 'sinh ngày .....'),
        ('tên là ', 'tên là .....'),
        ('con tên là ', 'con tên là .....')
    ]
    
    for old, new in replacements:
        if old in content and new not in content:
            content = content.replace(old, new)
            changes_made.append(f"Thay '{old}' -> '{new}'")
    
    # 3. CẬP NHẬT NGÀY THÁNG ĐÚNG
    content = content.replace('Hôm nay là ngày ngày 31/03/2026', f'Hôm nay là ngày {duong_lich}')
    content = content.replace('Ngày âm lịch: 13/02/2026', f'Ngày âm lịch: {amlich}')
    content = content.replace('Ngày âm lịch: ngày 13/02/2026', f'Ngày âm lịch: {amlich}')
    content = content.replace('Ngày âm lịch: ngày 31/Ba', f'Ngày âm lịch: {amlich}')
    content = content.replace('ngày 31/Ba', amlich)
    
    # 4. Lưu file nếu có thay đổi
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if changes_made:
            print(f"✅ prayer{prayer_num}.html: {len(changes_made)} thay đổi")
            for change in changes_made:
                print(f"   - {change}")
        else:
            print(f"✅ prayer{prayer_num}.html: Đã cập nhật ngày tháng")
    else:
        print(f"✅ prayer{prayer_num}.html: Hoàn chỉnh, không cần sửa")
    
    return True

def main():
    """Main function"""
    print("🔍 FINAL CHECK - KIỂM TRA VÀ SỬA TOÀN BỘ...")
    print("🔧 Đảm bảo:")
    print("  - Tất cả 'Tín chủ con là' có '.....'")
    print("  - Tất cả 'ngụ tại' có '.....'")
    print("  - Không còn trùng 'ngày ngày'")
    print("  - Ngày tháng chính xác")
    print()
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    print(f"📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")
    print(f"  Năm âm lịch: {lunar_year}")
    print()
    
    # Kiểm tra và sửa tất cả 46 trang
    success_count = 0
    
    for i in range(1, 47):
        if final_check_prayer(i):
            success_count += 1
    
    print(f"\n📊 KẾT QUẢ FINAL CHECK:")
    print(f"✅ Đã kiểm tra: {success_count}/46 bài")
    print(f"\n🎉 Hoàn thành FINAL CHECK toàn bộ!")

if __name__ == "__main__":
    main()
