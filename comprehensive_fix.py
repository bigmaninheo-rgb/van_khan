#!/usr/bin/env python3
"""
Script để KIỂM TRA và SỬA lại tất cả các bài văn khấn
Đảm bảo tất cả placeholder đều được thay thế và thêm "....." vào chỗ trống
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

def fix_prayer_comprehensive(prayer_num):
    """Sửa lại COMPREHENSIVE cho một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    
    print(f"🔍 Đang kiểm tra prayer{prayer_num}.html...")
    
    # 1. KIỂM TRA VÀ SỬA CÁC ĐỊNH DẠNG NGÀY SAI
    # Tìm tất cả các pattern ngày tháng sai
    old_patterns = [
        r'Hôm nay là ngày \d+/\d+/\d+',
        r'Ngày âm lịch: ngày \d+/\d+/\d+',
        r'Ngày âm lịch: ngày \d+/[A-Za-z]+',
        r'ngày \d+/[A-Za-z]+',
        r'Hôm nay là ngày \d+/[A-Za-z]+',
        r'Ngày dương lịch: ngày \d+/\d+/\d+'
    ]
    
    # Thay thế bằng định dạng đúng
    content = re.sub(r'Hôm nay là ngày \d+/\d+/\d+', f'Hôm nay là ngày {duong_lich}', content)
    content = re.sub(r'Ngày âm lịch: ngày \d+/\d+/\d+', f'Ngày âm lịch: {amlich}', content)
    content = re.sub(r'Ngày âm lịch: ngày \d+/[A-Za-z]+', f'Ngày âm lịch: {amlich}', content)
    content = re.sub(r'ngày \d+/[A-Za-z]+', amlich, content)
    content = re.sub(r'Hôm nay là ngày \d+/[A-Za-z]+', f'Hôm nay là ngày {duong_lich}', content)
    content = re.sub(r'Ngày dương lịch: ngày \d+/\d+/\d+', f'Ngày dương lịch: {duong_lich}', content)
    
    # 2. SỬA CÁC CHỖ TRỐNG - THÊM "....."
    # Pattern các chỗ trống cần thêm "....."
    patterns_to_fix = [
        (r'Vợ chồng con là\s+([^.\n]*?)\s+sinh được con', r'Vợ chồng con là ..... sinh được con'),
        (r'Vợ chồng con là\s+([^.\n]*?)\s+đặt tên là\s*$', r'Vợ chồng con là ..... đặt tên là .....'),
        (r'Chúng con ngụ tại:\s*$', r'Chúng con ngụ tại: .....'),
        (r'tên là\s+([^.\n]*?)\s+sinh ngày\s*$', r'tên là ..... sinh ngày .....'),
        (r'tên là\s+([^.\n]*?)\s+mẹ tròn con vuông', r'tên là ..... mẹ tròn con vuông'),
        (r'tên là\s+([^.\n]*?)\s+sinh được', r'tên là ..... sinh được'),
        (r'con tên là\s+([^.\n]*?)\s+sinh ngày', r'con tên là ..... sinh ngày'),
        (r'con tên là\s+([^.\n]*?)\s+mẹ tròn', r'con tên là ..... mẹ tròn'),
        (r'gia chủ tên là\s+([^.\n]*?)\s+cư ngụ', r'gia chủ tên là ..... cư ngụ'),
        (r'gia chủ tên là\s+([^.\n]*?)\s+ngụ tại', r'gia chủ tên là ..... ngụ tại'),
        (r'tên là\s*$', r'tên là .....'),
        (r'ngụ tại:\s*$', r'ngụ tại: .....'),
        (r'sinh ngày\s*$', r'sinh ngày .....'),
        (r'cư ngụ tại\s*$', r'cư ngụ tại .....'),
        (r'địa chỉ:\s*$', r'địa chỉ: .....'),
        (r'thông tin:\s*$', r'thông tin: .....')
    ]
    
    # Áp dụng tất cả patterns
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 3. SỬA CÁC DÒNG KẾT THÚC BẰNG SPACE/TRỐNG
    lines = content.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Các pattern kết thúc trống cần thêm "....."
        if any(stripped.endswith(pattern) for pattern in [
            'là ', 'tên là ', 'ngụ tại: ', 'sinh ngày ', 'cư ngụ tại ', 
            'địa chỉ: ', 'thông tin: ', 'là ..... sinh được', 'là ..... đặt'
        ]):
            # Đảm bảo không có "....." trùng lặp
            if not stripped.endswith('.....'):
                lines[i] = line.rstrip() + ' .....'
    
    content = '\n'.join(lines)
    
    # 4. CẬP NHẬT PLACEHOLDER CHUẨN
    content = re.sub(r'\[Ngày tháng dương lịch\]', duong_lich, content)
    content = re.sub(r'\[Ngày tháng âm lịch\]', amlich, content)
    content = re.sub(r'\[Năm\]', year, content)
    content = re.sub(r'\[Tên bé\/Tên gia chủ\]', '.....', content)
    content = re.sub(r'\[Địa chỉ\]', '.....', content)
    content = re.sub(r'\{ten_be\}', '.....', content)
    content = re.sub(r'\{dia_chi\}', '.....', content)
    content = re.sub(r'\{ngay_thang\}', duong_lich, content)
    content = re.sub(r'\{ngay_am_lich\}', amlich, content)
    
    # 5. Cập nhật JavaScript
    auto_update_script = f'''
        <script>
            // Tự động cập nhật ngày tháng vào bài văn khi load trang
            document.addEventListener('DOMContentLoaded', function() {{
                const prayerText = document.querySelector('.prayer-text');
                if (prayerText) {{
                    let text = prayerText.textContent;
                    // Cập nhật ngày tháng
                    text = text.replace(/\\[Ngày tháng dương lịch\\]/g, '{duong_lich}');
                    text = text.replace(/\\[Ngày tháng âm lịch\\]/g, '{amlich}');
                    text = text.replace(/\\[Năm\\]/g, '{year}');
                    // Cập nhật placeholder
                    text = text.replace(/\\[Tên bé\\/Tên gia chủ\\]/g, '.....');
                    text = text.replace(/\\[Địa chỉ\\]/g, '.....');
                    text = text.replace(/\\{{ten_be\\}}/g, '.....');
                    text = text.replace(/\\{{dia_chi\\}}/g, '.....');
                    text = text.replace(/\\{{ngay_thang\\}}/g, '{duong_lich}');
                    text = text.replace(/\\{{ngay_am_lich\\}}/g, '{amlich}');
                    
                    // Sửa các định dạng ngày sai
                    text = text.replace(/Hôm nay là ngày \\d+\\/\\d+\\/\\d+/g, 'Hôm nay là ngày {duong_lich}');
                    text = text.replace(/Ngày âm lịch: ngày \\d+\\/\\d+\\/\\d+/g, 'Ngày âm lịch: {amlich}');
                    text = text.replace(/Ngày âm lịch: ngày \\d+\\/[A-Za-z]+/g, 'Ngày âm lịch: {amlich}');
                    text = text.replace(/ngày \\d+\\/[A-Za-z]+/g, '{amlich}');
                    
                    // Sửa các chỗ trống
                    text = text.replace(/Vợ chồng con là\\s+sinh được con/g, 'Vợ chồng con là ..... sinh được con');
                    text = text.replace(/Chúng con ngụ tại:\\s*$/g, 'Chúng con ngụ tại: .....');
                    text = text.replace(/tên là\\s+sinh ngày\\s*$/g, 'tên là ..... sinh ngày .....');
                    text = text.replace(/tên là\\s*$/g, 'tên là .....');
                    
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
    
    # 6. KIỂM TRA LẠI KẾT QUẢ
    issues_found = []
    
    # Kiểm tra các pattern còn sót
    if re.search(r'Vợ chồng con là\s+[^.\n]*?\s+sinh được con[^.]*[^.....]', content):
        issues_found.append("Vẫn còn chỗ trống 'Vợ chồng con là'")
    
    if re.search(r'Chúng con ngụ tại:\s*$', content, re.MULTILINE):
        issues_found.append("Vẫn còn chỗ trống 'Chúng con ngụ tại:'")
    
    if re.search(r'tên là\s+[^.\n]*?\s+sinh ngày[^.]*[^.....]', content):
        issues_found.append("Vẫn còn chỗ trống 'tên là sinh ngày'")
    
    if re.search(r'ngày \d+/[A-Za-z]+', content):
        issues_found.append("Vẫn còn định dạng ngày sai")
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if issues_found:
        print(f"⚠️  prayer{prayer_num}.html: {', '.join(issues_found)}")
    else:
        print(f"✅ prayer{prayer_num}.html: Đã sửa hoàn chỉnh")
    
    return len(issues_found) == 0

def main():
    """Main function"""
    print("🔍 ĐANG KIỂM TRA VÀ SỬA TOÀN BỘ CÁC BÀI VĂN KHẤN...")
    print("🔧 Sửa:")
    print("  - Tất cả định dạng ngày tháng sai")
    print("  - Thêm '.....' vào mọi chỗ trống")
    print("  - Cập nhật JavaScript bảo vệ")
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
    issue_count = 0
    
    for i in range(1, 47):
        if fix_prayer_comprehensive(i):
            success_count += 1
        else:
            issue_count += 1
    
    print(f"\n📊 KẾT QUẢ KIỂM TRA:")
    print(f"✅ Hoàn chỉnh: {success_count}/46 bài")
    print(f"⚠️  Còn vấn đề: {issue_count}/46 bài")
    print(f"\n🎉 Hoàn thành kiểm tra toàn bộ!")

if __name__ == "__main__":
    main()
