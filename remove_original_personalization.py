#!/usr/bin/env python3
"""
Script để cập nhật các trang prayer gốc:
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

def update_original_prayer_page(file_name):
    """Cập nhật một trang prayer gốc"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/{file_name}")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    
    # 1. Xóa hoàn toàn phần "Tùy chỉnh thông tin"
    content = re.sub(
        r'<div class="personalization-form">.*?</div>\s*</div>\s*</div>\s*<div class="install-section">',
        '</div>\n        </div>\n        \n        <div class="install-section">',
        content,
        flags=re.DOTALL
    )
    
    # 2. Xóa tất cả JavaScript liên quan đến personalization
    content = re.sub(
        r'function personalizePrayer\(\) \{.*?\}\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
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
    
    content = re.sub(
        r'// Load settings từ localStorage.*?window\.addEventListener\(\'DOMContentLoaded\', function\(\) \{.*?\}\);',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 3. Tự động cập nhật ngày tháng vào bài khấn ngay khi mở trang
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
    
    content = re.sub(
        r'\[Địa chỉ\]',
        '',
        content
    )
    
    # 5. Thêm JavaScript để tự động cập nhật khi load trang
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
    
    print(f"✅ Đã cập nhật {file_name}")
    return True

def main():
    """Main function"""
    print("Đang cập nhật các trang prayer gốc...")
    print("🔧 Đồng bộ với các file prayer1.html đến prayer46.html")
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
        if update_original_prayer_page(file_name):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã cập nhật {success_count}/{len(original_files)} trang prayer gốc")
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    print(f"\n📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")

if __name__ == "__main__":
    main()
