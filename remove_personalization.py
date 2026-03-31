#!/usr/bin/env python3
"""
Script để cập nhật tất cả các trang prayer:
1. Xóa hoàn toàn phần "Tùy chỉnh thông tin"
2. Tự động cập nhật ngày tháng vào bài khấn
3. Xóa placeholder [Tên bé/Tên gia chủ] trong bài khấn
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

def update_prayer_page(prayer_num):
    """Cập nhật một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    
    # 1. Xóa hoàn toàn phần "Tùy chỉnh thông tin"
    # Tìm từ <div class="personalization-form"> đến </div> trước đó
    content = re.sub(
        r'<div class="personalization-form">.*?</div>\s*</div>\s*</div>\s*<div class="install-section">',
        '</div>\n        </div>\n        \n        <div class="install-section">',
        content,
        flags=re.DOTALL
    )
    
    # 2. Xóa tất cả JavaScript liên quan đến personalization
    # Xóa function personalizePrayer
    content = re.sub(
        r'function personalizePrayer\(\) \{.*?\}\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Xóa function copyPrayer và sharePrayer
    content = re.sub(
        r'function copyPrayer\(\) \{.*?\}\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'function sharePrayer\(\) \{.*?\}\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Xóa load settings từ localStorage
    content = re.sub(
        r'// Load settings từ localStorage.*?window\.addEventListener\(\'DOMContentLoaded\', function\(\) \{.*?\}\);',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 3. Tự động cập nhật ngày tháng vào bài khấn ngay khi mở trang
    # Thay thế placeholder ngay trong HTML
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
    
    # 4. Xóa hoàn toàn placeholder [Tên bé/Tên gia chủ]
    content = re.sub(
        r'\[Tên bé\/Tên gia chủ\]',
        '',
        content
    )
    
    # 5. Thay thế các placeholder khác nếu có
    content = re.sub(
        r'\[Địa chỉ\]',
        '',
        content
    )
    
    # 6. Thêm JavaScript để tự động cập nhật khi load trang
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
                    prayerText.textContent = text;
                }}
            }});
        </script>
'''
    
    # Chèn script trước </body>
    content = re.sub(
        r'</body>',
        auto_update_script + '\n</body>',
        content
    )
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã cập nhật prayer{prayer_num}.html")
    return True

def main():
    """Main function"""
    print("Đang cập nhật tất cả các trang prayer...")
    print("🔧 Thay đổi:")
    print("  - Xóa hoàn toàn phần 'Tùy chỉnh thông tin'")
    print("  - Tự động cập nhật ngày tháng vào bài khấn")
    print("  - Xóa placeholder [Tên bé/Tên gia chủ]")
    print()
    
    # Cập nhật tất cả 46 trang
    success_count = 0
    for i in range(1, 47):
        if update_prayer_page(i):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã cập nhật {success_count}/46 trang")
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    print(f"\n📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")

if __name__ == "__main__":
    main()
