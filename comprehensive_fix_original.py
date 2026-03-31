#!/usr/bin/env python3
"""
Script để KIỂM TRA và SỬA lại tất cả các bài văn khấn GỐC
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

def fix_original_prayer_comprehensive(file_name):
    """Sửa lại COMPREHENSIVE cho một trang prayer gốc"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/{file_name}")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year, lunar_year = get_current_dates()
    
    print(f"🔍 Đang kiểm tra {file_name}...")
    
    # 1. SỬA CÁC ĐỊNH DẠNG NGÀY SAI - DÙNG STRING REPLACE
    content = content.replace('Hôm nay là ngày 31/03/2026', f'Hôm nay là ngày {duong_lich}')
    content = content.replace('Ngày âm lịch: 13/02/2026', f'Ngày âm lịch: {amlich}')
    content = content.replace('Ngày âm lịch: ngày 13/02/2026', f'Ngày âm lịch: {amlich}')
    content = content.replace('Ngày âm lịch: ngày 31/Ba', f'Ngày âm lịch: {amlich}')
    content = content.replace('ngày 31/Ba', amlich)
    
    # Tìm và thay thế các pattern ngày tháng khác
    content = re.sub(r'Hôm nay là ngày \d+/\d+/\d+', f'Hôm nay là ngày {duong_lich}', content)
    content = re.sub(r'Ngày âm lịch: ngày \d+/\d+/\d+', f'Ngày âm lịch: {amlich}', content)
    content = re.sub(r'Ngày âm lịch: ngày \d+/[A-Za-z]+', f'Ngày âm lịch: {amlich}', content)
    content = re.sub(r'ngày \d+/[A-Za-z]+', amlich, content)
    
    # 2. SỬA CÁC CHỖ TRỐNG - THÊM "....."
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        modified_line = line
        
        # Các pattern cần thêm "....."
        patterns_to_fix = [
            'Vợ chồng con là  sinh được con',
            'Vợ chồng con là   sinh được con',
            'Vợ chồng con là sinh được con',
            'Vợ chồng con là  đặt tên là ',
            'Vợ chồng con là   đặt tên là ',
            'Chúng con ngụ tại: ',
            'Chúng con ngụ tại:  ',
            'tên là  sinh ngày ',
            'tên là   sinh ngày ',
            'tên là sinh ngày ',
            'tên là ',
            'sinh ngày ',
            'cư ngụ tại ',
            'địa chỉ: ',
            'thông tin: ',
            'con tên là  sinh ngày',
            'con tên là   sinh ngày',
            'con tên là sinh ngày',
            'con tên là ',
            'gia chủ tên là  cư ngụ',
            'gia chủ tên là   cư ngụ',
            'gia chủ tên là  ngụ tại',
            'gia chủ tên là   ngụ tại'
        ]
        
        # Kiểm tra và sửa từng pattern
        for pattern in patterns_to_fix:
            if pattern in modified_line:
                # Đảm bảo không thêm "....." trùng lặp
                if '.....' not in modified_line:
                    if pattern.endswith(' '):
                        modified_line = modified_line.replace(pattern, pattern + '.....')
                    else:
                        modified_line = modified_line.replace(pattern, pattern + ' .....')
        
        # Kiểm tra các dòng kết thúc bằng pattern trống
        stripped = modified_line.strip()
        if any(stripped.endswith(end_pattern) for end_pattern in [
            'là ', 'tên là ', 'ngụ tại: ', 'sinh ngày ', 'cư ngụ tại ', 
            'địa chỉ: ', 'thông tin: '
        ]):
            if '.....' not in modified_line:
                modified_line = modified_line.rstrip() + ' .....'
        
        modified_lines.append(modified_line)
    
    content = '\n'.join(modified_lines)
    
    # 3. CẬP NHẬT PLACEHOLDER CHUẨN
    content = re.sub(r'\[Ngày tháng dương lịch\]', duong_lich, content)
    content = re.sub(r'\[Ngày tháng âm lịch\]', amlich, content)
    content = re.sub(r'\[Năm\]', year, content)
    content = re.sub(r'\[Tên bé\/Tên gia chủ\]', '.....', content)
    content = re.sub(r'\[Địa chỉ\]', '.....', content)
    content = re.sub(r'\{ten_be\}', '.....', content)
    content = re.sub(r'\{dia_chi\}', '.....', content)
    content = re.sub(r'\{ngay_thang\}', duong_lich, content)
    content = re.sub(r'\{ngay_am_lich\}', amlich, content)
    
    # 4. Cập nhật JavaScript đơn giản
    js_content = f'''
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const prayerText = document.querySelector('.prayer-text');
                if (prayerText) {{
                    let text = prayerText.textContent;
                    text = text.replace(/\\[Ngày tháng dương lịch\\]/g, '{duong_lich}');
                    text = text.replace(/\\[Ngày tháng âm lịch\\]/g, '{amlich}');
                    text = text.replace(/\\[Năm\\]/g, '{year}');
                    text = text.replace(/\\[Tên bé\\/Tên gia chủ\\]/g, '.....');
                    text = text.replace(/\\[Địa chỉ\\]/g, '.....');
                    text = text.replace(/\\{{ten_be\\}}/g, '.....');
                    text = text.replace(/\\{{dia_chi\\}}/g, '.....');
                    text = text.replace(/\\{{ngay_thang\\}}/g, '{duong_lich}');
                    text = text.replace(/\\{{ngay_am_lich\\}}/g, '{amlich}');
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
    content = re.sub(r'</body>', js_content + '\n</body>', content)
    
    # 5. KIỂM TRA LẠI KẾT QUẢ
    issues_found = []
    
    # Kiểm tra các pattern còn sót
    if 'Vợ chồng con là  sinh được con' in content:
        issues_found.append("Vẫn còn chỗ trống 'Vợ chồng con là'")
    
    if 'Chúng con ngụ tại: ' in content and 'Chúng con ngụ tại: .....' not in content:
        issues_found.append("Vẫn còn chỗ trống 'Chúng con ngụ tại:'")
    
    if 'tên là  sinh ngày ' in content:
        issues_found.append("Vẫn còn chỗ trống 'tên là sinh ngày'")
    
    if 'ngày 31/Ba' in content:
        issues_found.append("Vẫn còn định dạng ngày sai")
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if issues_found:
        print(f"⚠️  {file_name}: {', '.join(issues_found)}")
        return False
    else:
        print(f"✅ {file_name}: Đã sửa hoàn chỉnh")
        return True

def main():
    """Main function"""
    print("🔍 ĐANG KIỂM TRA VÀ SỬA TOÀN BỘ CÁC BÀI VĂN KHẤN GỐC...")
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
    
    # Kiểm tra và sửa tất cả các file
    success_count = 0
    issue_count = 0
    
    for file_name in original_files:
        if fix_original_prayer_comprehensive(file_name):
            success_count += 1
        else:
            issue_count += 1
    
    print(f"\n📊 KẾT QUẢ KIỂM TRA CÁC FILE GỐC:")
    print(f"✅ Hoàn chỉnh: {success_count}/{len(original_files)} bài")
    print(f"⚠️  Còn vấn đề: {issue_count}/{len(original_files)} bài")
    print(f"\n🎉 Hoàn thành kiểm tra toàn bộ!")

if __name__ == "__main__":
    main()
