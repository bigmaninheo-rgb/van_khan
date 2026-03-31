#!/usr/bin/env python3
"""
Script để sửa lại tất cả các trang prayer:
1. Xóa tất cả {ten_be} trong bài khấn
2. Đảm bảo ngày tháng tự động cập nhật
"""

import re
from pathlib import Path
from datetime import datetime, date

def get_current_dates():
    """Lấy ngày tháng hiện tại"""
    today = date.today()
    
    # Dương lịch
    duong_lich = today.strftime("ngày %d/%m/%Y")
    
    # Âm lịch (tạm dùng đơn giản)
    amlich_months = ['Giêng', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 
                    'Bảy', 'Tám', 'Chín', 'Mười', 'Mười Một', 'Chạp']
    
    amlich_day = today.day
    amlich_month_idx = (today.month - 1) % 12
    amlich_month = amlich_months[amlich_month_idx]
    
    amlich = f"ngày {amlich_day}/{amlich_month}"
    
    return duong_lich, amlich, str(today.year)

def fix_prayer_page(prayer_num):
    """Sửa một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    
    # 1. Xóa tất cả {ten_be} trong bài khấn
    content = re.sub(
        r'\{ten_be\}',
        '',
        content
    )
    
    # 2. Xóa tất cả {ngay_thang}, {ngay_am_lich}, {ten_be} khác
    content = re.sub(
        r'\{ngay_thang\}',
        duong_lich,
        content
    )
    
    content = re.sub(
        r'\{ngay_am_lich\}',
        amlich,
        content
    )
    
    # 3. Xóa các placeholder khác
    content = re.sub(
        r'\{dia_chi\}',
        '',
        content
    )
    
    content = re.sub(
        r'\{ten_be\}',
        '',
        content
    )
    
    # 4. Cập nhật JavaScript để xử lý cả {ten_be}
    auto_update_script = f'''
        <script>
            // Tự động cập nhật ngày tháng vào bài văn khi load trang
            document.addEventListener('DOMContentLoaded', function() {{
                const prayerText = document.querySelector('.prayer-text');
                if (prayerText) {{
                    let text = prayerText.textContent;
                    text = text.replace(/\\{{ngay_thang\\}}/g, '{duong_lich}');
                    text = text.replace(/\\{{ngay_am_lich\\}}/g, '{amlich}');
                    text = text.replace(/\\{{ten_be\\}}/g, '');
                    text = text.replace(/\\{{dia_chi\\}}/g, '');
                    text = text.replace(/\\[Ngày tháng dương lịch\\]/g, '{duong_lich}');
                    text = text.replace(/\\[Ngày tháng âm lịch\\]/g, '{amlich}');
                    text = text.replace(/\\[Tên bé\\/Tên gia chủ\\]/g, '');
                    text = text.replace(/\\[Địa chỉ\\]/g, '');
                    prayerText.textContent = text;
                }}
            }});
        </script>
'''
    
    # Xóa script cũ nếu có
    content = re.sub(
        r'<script>\s*// Tự động cập nhật ngày tháng vào bài văn khi load trang.*?</script>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Chèn script mới trước </body>
    content = re.sub(
        r'</body>',
        auto_update_script + '\n</body>',
        content
    )
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã sửa prayer{prayer_num}.html")
    return True

def main():
    """Main function"""
    print("Đang sửa lại tất cả các trang prayer...")
    print("🔧 Thay đổi:")
    print("  - Xóa tất cả {ten_be} trong bài khấn")
    print("  - Đảm bảo ngày tháng tự động cập nhật")
    print()
    
    # Cập nhật tất cả 46 trang
    success_count = 0
    for i in range(1, 47):
        if fix_prayer_page(i):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã sửa {success_count}/46 trang")
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    print(f"\n📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")

if __name__ == "__main__":
    main()
