#!/usr/bin/env python3
"""
Script để cập nhật các trang prayer gốc (prayerI_001.html, prayerII_006.html, etc.)
để đồng bộ với các file prayer1.html đến prayer46.html
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
    
    # 1. Xóa trường "Tên bé / Tên gia chủ"
    content = re.sub(
        r'<div class="form-group">\s*<label for="ten_be">Tên bé / Tên gia chủ:</label>\s*<input type="text" id="ten_be" placeholder="Nhập tên bé hoặc tên gia chủ">\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 2. Tự động điền ngày tháng dương lịch
    content = re.sub(
        r'<input type="text" id="ngay_thang" placeholder="ngày 25/12/2025">',
        f'<input type="text" id="ngay_thang" value="{duong_lich}" readonly style="background: #f8f9fa;">',
        content
    )
    
    # 3. Tự động điền ngày tháng âm lịch
    content = re.sub(
        r'<input type="text" id="ngay_am_lich" placeholder="ngày 01/11/Ất Dần">',
        f'<input type="text" id="ngay_am_lich" value="{amlich}" readonly style="background: #f8f9fa;">',
        content
    )
    
    # 4. Tự động điền năm
    content = re.sub(
        r'<input type="number" id="nam" placeholder="2025">',
        f'<input type="number" id="nam" value="{year}" readonly style="background: #f8f9fa;">',
        content
    )
    
    # 5. Cập nhật JavaScript
    content = re.sub(
        r'if \(!tenBe\) {\s*alert\(\'Vui lòng nhập tên bé hoặc tên gia chủ\'\);\s*return;\s*}',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'prayerText\.replace\(/\\\[Tên bé\/Tên gia chủ\\\]/g, tenBe\)',
        'prayerText.replace(/\\[Tên bé\/Tên gia chủ\\]/g, "...")',
        content
    )
    
    # 6. Cập nhật localStorage
    content = re.sub(
        r'localStorage\.setItem\(\'van_khan_settings\', JSON\.stringify\(\{\s*ten_be: tenBe,\s*dia_chi: diaChi,\s*ngay_thang: ngayThang,\s*ngay_am_lich: ngayAmLich,\s*nam: nam\s*\}\)\);',
        'localStorage.setItem(\'van_khan_settings\', JSON.stringify({\n                        dia_chi: diaChi,\n                        ngay_thang: ngayThang,\n                        ngay_am_lich: ngayAmLich,\n                        nam: nam\n                    }));',
        content
    )
    
    # 7. Cập nhật load settings
    content = re.sub(
        r'document\.getElementById\(\'ten_be\'\)\.value = parsed\.ten_be \|\| \'\';',
        '',
        content
    )
    
    content = re.sub(
        r'if \(parsed\.ten_be\) {',
        'if (parsed.dia_chi || parsed.ngay_thang) {',
        content
    )
    
    # 8. Cập nhật label và placeholder
    content = re.sub(
        r'<label for="dia_chi">Địa chỉ:</label>',
        '<label for="dia_chi">Địa chỉ (nếu cần):</label>',
        content
    )
    
    content = re.sub(
        r'<input type="text" id="dia_chi" placeholder="Nhập địa chỉ nhà">',
        '<input type="text" id="dia_chi" placeholder="Nhập địa chỉ nhà (nếu cần)">',
        content
    )
    
    content = re.sub(
        r'<h3>📝 Tùy chỉnh thông tin cá nhân</h3>',
        '<h3>📝 Tùy chỉnh thông tin</h3>',
        content
    )
    
    # 9. Thay placeholder trong template
    content = re.sub(
        r'\[Tên bé\/Tên gia chủ\]',
        '...',
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
