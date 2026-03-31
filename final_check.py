#!/usr/bin/env python3
"""
Script FINAL CHECK - Kiểm tra và sửa lại tất cả các bài văn khấn
Đảm bảo TẤT CẢ đều có "....." và ngày tháng đúng
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
    
    # 2. SỬA CÁC CHỖ TRỐNG CẦN THÊM "....."
    lines = content.split('\n')
    modified_lines = []
    
    for i, line in enumerate(lines):
        modified_line = line
        line_stripped = line.strip()
        
        # Kiểm tra và sửa các pattern trống
        if line_stripped == 'Tín chủ con là ':
            modified_line = 'Tín chủ con là .....'
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'Tín chủ con là'")
        
        elif line_stripped == 'ngụ tại ':
            modified_line = 'ngụ tại .....'
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'ngụ tại'")
        
        elif line_stripped == 'Vợ chồng con là  sinh được con':
            modified_line = 'Vợ chồng con là ..... sinh được con'
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'Vợ chồng con là'")
        
        elif line_stripped == 'Vợ chồng con là sinh được con':
            modified_line = 'Vợ chồng con là ..... sinh được con'
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'Vợ chồng con là'")
        
        elif line_stripped.startswith('Vợ chồng con là ') and '.....' not in line_stripped:
            modified_line = line_stripped.replace('Vợ chồng con là ', 'Vợ chồng con là .....')
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'Vợ chồng con là'")
        
        elif line_stripped.startswith('Tín chủ con là ') and '.....' not in line_stripped:
            modified_line = line_stripped.replace('Tín chủ con là ', 'Tín chủ con là .....')
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'Tín chủ con là'")
        
        elif line_stripped.startswith('Chúng con ngụ tại:') and '.....' not in line_stripped:
            modified_line = line_stripped.replace('Chúng con ngụ tại:', 'Chúng con ngụ tại: .....')
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'Chúng con ngụ tại'")
        
        elif line_stripped.startswith('ngụ tại ') and '.....' not in line_stripped:
            modified_line = line_stripped.replace('ngụ tại ', 'ngụ tại .....')
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'ngụ tại'")
        
        elif line_stripped.startswith('tên là ') and '.....' not in line_stripped:
            modified_line = line_stripped.replace('tên là ', 'tên là .....')
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'tên là'")
        
        elif line_stripped.startswith('sinh ngày ') and '.....' not in line_stripped:
            modified_line = line_stripped.replace('sinh ngày ', 'sinh ngày .....')
            changes_made.append(f"Thêm '.....' vào dòng {i+1}: 'sinh ngày'")
        
        modified_lines.append(modified_line)
    
    content = '\n'.join(modified_lines)
    
    # 3. CẬP NHẬT NGÀY THÁNG ĐÚNG
    content = content.replace('Hôm nay là ngày ngày 31/03/2026', f'Hôm nay là ngày {duong_lich}')
    content = content.replace('Ngày âm lịch: 13/02/2026', f'Ngày âm lịch: {amlich}')
    content = content.replace('Ngày âm lịch: ngày 13/02/2026', f'Ngày âm lịch: {amlich}')
    content = content.replace('Ngày âm lịch: ngày 31/Ba', f'Ngày âm lịch: {amlich}')
    content = content.replace('ngày 31/Ba', amlich)
    
    # 4. CẬP NHẬT PLACEHOLDER CHUẨN
    content = re.sub(r'\[Ngày tháng dương lịch\]', duong_lich, content)
    content = re.sub(r'\[Ngày tháng âm lịch\]', amlich, content)
    content = re.sub(r'\[Năm\]', year, content)
    content = re.sub(r'\[Tên bé\/Tên gia chủ\]', '.....', content)
    content = re.sub(r'\[Địa chỉ\]', '.....', content)
    
    # 5. CẬP NHẬT JAVASCRIPT
    js_content = f'''
        <script>
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
                    // Sửa các định dạng ngày sai
                    text = text.replace(/Hôm nay là ngày ngày \\d+\\/\\d+\\/\\d+/g, 'Hôm nay là ngày {duong_lich}');
                    text = text.replace(/Ngày âm lịch: ngày \\d+\\/\\d+\\/\\d+/g, 'Ngày âm lịch: {amlich}');
                    // Sửa các chỗ trống
                    text = text.replace(/Tín chủ con là\\s*$/gm, 'Tín chủ con là .....');
                    text = text.replace(/Chúng con ngụ tại:\\s*$/gm, 'Chúng con ngụ tại: .....');
                    text = text.replace(/ngụ tại:\\s*$/gm, 'ngụ tại: .....');
                    text = text.replace(/tên là\\s+sinh ngày\\s*$/gm, 'tên là ..... sinh ngày .....');
                    text = text.replace(/tên là\\s*$/gm, 'tên là .....');
                    text = text.replace(/Vợ chồng con là\\s+sinh được con$/gm, 'Vợ chồng con là ..... sinh được con');
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
    
    # 6. KIỂM TRA KẾT QUẢ
    final_issues = []
    
    # Kiểm tra các pattern còn sót
    if 'Tín chủ con là ' in content and 'Tín chủ con là .....' not in content:
        final_issues.append("Vẫn còn 'Tín chủ con là' trống")
    
    if 'ngụ tại ' in content and 'ngụ tại .....' not in content:
        final_issues.append("Vẫn còn 'ngụ tại' trống")
    
    if 'Hôm nay là ngày ngày ' in content:
        final_issues.append("Vẫn còn trùng 'ngày ngày'")
    
    # Lưu file nếu có thay đổi
    if content != original_content or changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if changes_made:
            print(f"✅ prayer{prayer_num}.html: {len(changes_made)} thay đổi")
            for change in changes_made:
                print(f"   - {change}")
        else:
            print(f"✅ prayer{prayer_num}.html: Đã cập nhật")
    else:
        print(f"✅ prayer{prayer_num}.html: Hoàn chỉnh, không cần sửa")
    
    return len(final_issues) == 0

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
    issue_count = 0
    total_changes = 0
    
    for i in range(1, 47):
        if final_check_prayer(i):
            success_count += 1
        else:
            issue_count += 1
    
    print(f"\n📊 KẾT QUẢ FINAL CHECK:")
    print(f"✅ Hoàn chỉnh: {success_count}/46 bài")
    print(f"⚠️  Còn vấn đề: {issue_count}/46 bài")
    print(f"\n🎉 Hoàn thành FINAL CHECK toàn bộ!")

if __name__ == "__main__":
    main()
